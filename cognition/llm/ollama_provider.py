"""Ollama LLM provider."""
import json
import os
from typing import Dict, Any

import httpx

from core.config import settings
from cognition.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout_s = float(os.getenv("OLLAMA_TIMEOUT_S", "15"))

    def complete_json(self, prompt: str, system: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": f"{system}\n\n{prompt}",
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        text = data.get("response", "{}").strip()
        return json.loads(text)
