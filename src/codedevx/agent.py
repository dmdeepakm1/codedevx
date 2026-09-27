from codedevx.config import settings
from codedevx.llm.router import ProviderRouter
from codedevx.vector.qdrant_store import QdrantCodeStore

SYSTEM = """You are CodeDevX, an engineering assistant.
Answer only from supplied repository context when making claims about code.
Identify repository and file paths for important findings.
Distinguish evidence from inference.
If context is insufficient, say what additional repository/file should be searched.
Do not invent classes, APIs, tests, dependencies, or behavior."""

class EngineeringAgent:
    def __init__(self):
        self.vector=QdrantCodeStore()
        self.router=ProviderRouter()

    def ask(self, project_id: str, question: str, provider: str="openai") -> str:
        hits=self.vector.search(project_id,question,limit=settings.max_context_chunks)
        context_parts=[f"REPO: {h['repo_id']}\nFILE: {h['path']}:{h['start_line']}-{h['end_line']}\nSYMBOL: {h['symbol']}\nCODE:\n{h['content']}" for h in hits]
        context="\n\n---\n\n".join(context_parts)
        prompt=f"PROJECT: {project_id}\n\nQUESTION:\n{question}\n\nRETRIEVED CODE CONTEXT:\n{context or '[none]'}"
        return self.router.provider(provider).generate(SYSTEM,prompt).text
