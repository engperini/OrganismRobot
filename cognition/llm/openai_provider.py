"""OpenAI LLM provider."""
import json
import os
from typing import Dict, Any

from openai import OpenAI

from cognition.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        self.model = os.getenv("OPENAI_MODEL", "gpt-5.2")
        self.client = OpenAI(api_key=api_key)

    def complete_json(self, prompt: str, system: str) -> Dict[str, Any]:
        response = self.client.responses.create(
            model=self.model,
            instructions=system,
            input=prompt,
        )

        text = response.output_text.strip()
        return json.loads(text)
