
import json
from openai import OpenAI

from core.config import settings
from cognition.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def complete_json(self, prompt: str, system: str):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
        )

        text = response.choices[0].message.content
        return json.loads(text)
