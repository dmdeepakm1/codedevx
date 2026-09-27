from openai import OpenAI
from codedevx.config import settings
from codedevx.llm.base import LLMProvider, LLMResult

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, system: str, user: str) -> LLMResult:
        response = self.client.responses.create(model=settings.openai_model, instructions=system, input=user)
        return LLMResult(text=response.output_text, provider="openai", model=settings.openai_model)
