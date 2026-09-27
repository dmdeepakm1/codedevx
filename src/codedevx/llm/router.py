from codedevx.llm.base import LLMProvider
from codedevx.llm.openai_provider import OpenAIProvider

class ProviderRouter:
    """Central routing point for OpenAI now and Claude/Ollama/llama.cpp later."""
    def provider(self, requested: str = "openai") -> LLMProvider:
        if requested == "openai":
            return OpenAIProvider()
        raise ValueError(f"Provider not configured: {requested}")
