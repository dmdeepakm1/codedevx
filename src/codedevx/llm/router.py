from codedevx.llm.base import LLMProvider
from codedevx.llm.openai_provider import OpenAIProvider
from codedevx.llm.ollama_provider import OllamaProvider
from codedevx.llm.anthropic_provider import AnthropicProvider

class ProviderRouter:
    def provider(self,requested:str="openai")->LLMProvider:
        requested=requested.lower().strip()
        if requested=="openai":return OpenAIProvider()
        if requested=="ollama":return OllamaProvider()
        if requested in {"anthropic","claude"}:return AnthropicProvider()
        raise ValueError(f"Provider not configured: {requested}")
