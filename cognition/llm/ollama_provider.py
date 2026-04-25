"""Ollama LLM provider."""

import json
import httpx

from core.config import settings
from cognition.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

    def complete_json(self, prompt: str, system: str):
        payload = {
            "model": self.model,
            "prompt": f"{system}\n\n{prompt}",
            "stream": False,
            "format": "json",
        }

        response = httpx.post(f"{self.url}/api/generate", json=payload, timeout=60.0)
        response.raise_for_status()

        data = response.json()
        return json.loads(data["response"])

