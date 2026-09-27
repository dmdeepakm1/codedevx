from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMResult:
    text: str
    provider: str
    model: str

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user: str) -> LLMResult:
        raise NotImplementedError
