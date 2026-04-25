"""Mock LLM provider for offline development."""
from typing import Dict, Any
from cognition.llm.base import LLMProvider


class MockProvider(LLMProvider):
    def complete_json(self, prompt: str, system: str) -> Dict[str, Any]:
        return {
            "assessment": "Mock brain active. I am observing the environment safely.",
            "intent": "idle",
            "strategy": ["wait", "observe"],
            "mood": "bored",
            "store_candidate": False,
            "why_store": None,
        }
