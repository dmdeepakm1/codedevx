from openai import OpenAI
from codedevx.config import settings
from codedevx.embeddings.base import EmbeddingProvider

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when CODEDEVX_EMBEDDING_PROVIDER=openai")
        self.client=OpenAI(api_key=settings.openai_api_key)

    def embed(self,texts:list[str])->list[list[float]]:
        response=self.client.embeddings.create(model=settings.embedding_model,input=texts)
        return [item.embedding for item in response.data]
