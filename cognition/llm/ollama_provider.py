"""Ollama LLM provider."""
import json
import os
from typing import Dict, Any

import httpx

from cognition.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")

    def complete_json(self, prompt: str, system: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": f"{system}\n\n{prompt}",
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        text = data.get("response", "{}").strip()
        return json.loads(text)
