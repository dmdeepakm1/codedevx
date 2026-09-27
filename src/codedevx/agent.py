from codedevx.config import settings
from codedevx.context import ContextBudget, estimate_tokens, evidence_context
from codedevx.llm.router import ProviderRouter
from codedevx.retrieval.hybrid import HybridRetriever
from codedevx.storage.sql import profiles_for_project
from codedevx.vector.qdrant_store import QdrantCodeStore

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
        profiles=profiles_for_project(project_id)
        budget=ContextBudget(max_tokens=settings.max_context_tokens)
        header=f"PROFILE: V{settings.version}\nPROJECT: {project_id}\nQUESTION:\n{question}\n\nEVIDENCE:\n"
        if estimate_tokens(header) > min(budget.requirement, budget.max_tokens):
            raise ValueError("Question exceeds configured requirement/context token budget")
        context=evidence_context(hits,graph,profiles,budget,estimate_tokens(header)+estimate_tokens(SYSTEM))
        prompt=header+context
        return self.router.provider(provider).generate(SYSTEM,prompt).text
