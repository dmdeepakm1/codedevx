import httpx
from codedevx.config import settings
from codedevx.embeddings.base import EmbeddingProvider

class OllamaEmbeddingProvider(EmbeddingProvider):
    def embed(self,texts:list[str])->list[list[float]]:
        vectors=[]
        for text in texts:
            response=httpx.post(
                f"{settings.ollama_url}/api/embed",
                json={"model":settings.ollama_embedding_model,"input":text},
                timeout=settings.llm_timeout_seconds,
            )
            response.raise_for_status()
            payload=response.json()
            embeddings=payload.get("embeddings") or []
            if not embeddings:
                raise RuntimeError("Ollama returned no embedding")
            vectors.append(embeddings[0])
        return vectors
