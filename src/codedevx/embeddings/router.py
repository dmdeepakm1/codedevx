from codedevx.config import settings
from codedevx.embeddings.base import EmbeddingProvider
from codedevx.embeddings.openai_provider import OpenAIEmbeddingProvider
from codedevx.embeddings.ollama_provider import OllamaEmbeddingProvider

class EmbeddingRouter:
    def provider(self,requested:str|None=None)->EmbeddingProvider:
        name=(requested or settings.embedding_provider).lower().strip()
        if name=="openai":return OpenAIEmbeddingProvider()
        if name=="ollama":return OllamaEmbeddingProvider()
        raise ValueError(f"Embedding provider not configured: {name}")
