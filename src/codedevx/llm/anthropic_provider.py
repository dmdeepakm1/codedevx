from anthropic import Anthropic
from codedevx.config import settings
from codedevx.llm.base import LLMProvider, LLMResult

class AnthropicProvider(LLMProvider):
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required only when CodeDevX calls Anthropic directly. It is not required when Claude is an external MCP client.")
        self.client=Anthropic(api_key=settings.anthropic_api_key)

    def generate(self, system: str, user: str) -> LLMResult:
        response=self.client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=system,
            messages=[{"role":"user","content":user}],
        )
        text="".join(block.text for block in response.content if getattr(block,"type","")=="text")
        return LLMResult(text=text,provider="anthropic",model=settings.anthropic_model)
