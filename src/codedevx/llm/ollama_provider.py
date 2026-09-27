import httpx
from codedevx.config import settings
from codedevx.llm.base import LLMProvider, LLMResult

class OllamaProvider(LLMProvider):
    def generate(self, system: str, user: str) -> LLMResult:
        r=httpx.post(f"{settings.ollama_url}/api/chat",json={"model":settings.ollama_model,"messages":[{"role":"system","content":system},{"role":"user","content":user}],"stream":False},timeout=settings.llm_timeout_seconds)
        r.raise_for_status()
        return LLMResult(text=r.json()["message"]["content"],provider="ollama",model=settings.ollama_model)
