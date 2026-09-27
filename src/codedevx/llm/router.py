from codedevx.llm.base import LLMProvider
from codedevx.llm.openai_provider import OpenAIProvider
from codedevx.llm.ollama_provider import OllamaProvider
class ProviderRouter:
    def provider(self,requested:str="openai")->LLMProvider:
        if requested=="openai":return OpenAIProvider()
        if requested=="ollama":return OllamaProvider()
        raise ValueError(f"Provider not configured: {requested}")
