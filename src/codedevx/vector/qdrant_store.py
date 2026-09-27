from qdrant_client import QdrantClient, models
from openai import OpenAI
from codedevx.config import settings
from codedevx.domain import CodeChunk

class QdrantCodeStore:
    def __init__(self):
        self.q = QdrantClient(url=settings.qdrant_url)
        self.openai = OpenAI(api_key=settings.openai_api_key)
        self.collection = settings.qdrant_collection

    def _embed(self, texts: list[str]) -> list[list[float]]:
        r = self.openai.embeddings.create(model=settings.embedding_model, input=texts)
        return [x.embedding for x in r.data]

    def _ensure(self, dim: int):
        if not self.q.collection_exists(self.collection):
            self.q.create_collection(collection_name=self.collection, vectors_config=models.VectorParams(size=dim,distance=models.Distance.COSINE))

    def upsert(self, chunks: list[CodeChunk]):
        if not chunks:
            return
        vectors = self._embed([f"{c.language}\n{c.relative_path}\n{c.symbol}\n{c.content}" for c in chunks])
        self._ensure(len(vectors[0]))
        import uuid
        points=[]
        for c,v in zip(chunks,vectors):
            points.append(models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL,c.stable_id)),vector=v,payload={"stable_id":c.stable_id,"project_id":c.project_id,"repo_id":c.repo_id,"path":c.relative_path,"language":c.language,"symbol":c.symbol,"start_line":c.start_line,"end_line":c.end_line,"content":c.content,"content_hash":c.content_hash}))
        self.q.upsert(collection_name=self.collection,points=points)

    def search(self, project_id: str, query: str, limit: int = 12) -> list[dict]:
        vector=self._embed([query])[0]
        if not self.q.collection_exists(self.collection):
            return []
        hits=self.q.query_points(collection_name=self.collection,query=vector,query_filter=models.Filter(must=[models.FieldCondition(key="project_id",match=models.MatchValue(value=project_id))]),limit=limit,with_payload=True).points
        return [{"score":h.score,**(h.payload or {})} for h in hits]
