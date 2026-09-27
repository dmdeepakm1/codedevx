from codedevx.config import settings
from codedevx.llm.router import ProviderRouter
from codedevx.vector.qdrant_store import QdrantCodeStore
from codedevx.retrieval.hybrid import HybridRetriever

SYSTEM="""You are CodeDevX, an engineering assistant.
Use supplied evidence for claims about the project. Cite repository/file locations from context.
Distinguish evidence from inference. If evidence is insufficient, say what must be retrieved.
Never invent classes, APIs, tests, dependencies, incidents, tickets, or documentation."""

class EngineeringAgent:
    def __init__(self):
        self.vector=QdrantCodeStore()
        self.hybrid=HybridRetriever()
        self.router=ProviderRouter()

    def ask(self,project_id:str,question:str,provider:str="openai")->str:
        if settings.version >= 2:
            retrieved=self.hybrid.retrieve(project_id,question,settings.max_context_chunks)
            hits=retrieved["vector"]
            graph=retrieved["graph"]
        else:
            hits=self.vector.search(project_id,question,settings.max_context_chunks)
            graph=[]
        context=[]
        for h in hits:
            context.append(f"SOURCE: {h.get('repo_id')}\nPATH: {h.get('path')}:{h.get('start_line')}-{h.get('end_line')}\nSYMBOL/TITLE: {h.get('symbol')}\nCONTENT:\n{h.get('content')}")
        if graph:
            context.append("GRAPH EVIDENCE:\n"+str(graph))
        prompt=f"PROFILE: V{settings.version}\nPROJECT: {project_id}\nQUESTION:\n{question}\n\nEVIDENCE:\n"+("\n\n---\n\n".join(context) or "[none]")
        return self.router.provider(provider).generate(SYSTEM,prompt).text
