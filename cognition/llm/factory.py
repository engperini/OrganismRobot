"""Factory for selecting the active LLM provider."""
from core.config import settings
from cognition.llm.base import LLMProvider
from cognition.llm.mock_provider import MockProvider


def get_llm_provider() -> LLMProvider:
    provider = settings.LLM_PROVIDER.lower()

    if provider == "mock":
        return MockProvider()

    if provider == "openai":
        from cognition.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()

    if provider == "ollama":
        from cognition.llm.ollama_provider import OllamaProvider
        return OllamaProvider()

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
