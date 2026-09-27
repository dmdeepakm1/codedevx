import re
from codedevx.config import settings
from codedevx.vector.qdrant_store import QdrantCodeStore

class HybridRetriever:
    def __init__(self):
        self.vector=QdrantCodeStore()

    def retrieve(self,project_id:str,query:str,limit:int|None=None)->dict:
        limit=limit or settings.max_context_chunks
        vector=self.vector.search(project_id,query,limit)
        graph=[]
        if settings.graph_enabled:
            try:
                from codedevx.graph.neo4j_store import Neo4jGraphStore
                terms=[x for x in re.findall(r"[A-Za-z_][A-Za-z0-9_.-]+",query) if len(x)>2][:8]
                g=Neo4jGraphStore()
                graph=g.neighbors(project_id,terms,limit)
                g.close()
            except Exception as exc:
                if settings.strict_integrations:
                    raise
                graph=[{"warning":f"graph unavailable: {type(exc).__name__}"}]
        return {"vector":vector,"graph":graph}
