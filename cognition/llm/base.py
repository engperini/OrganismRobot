"""LLM provider abstractions."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    def complete_json(self, prompt: str, system: str) -> Dict[str, Any]:
        raise NotImplementedError
