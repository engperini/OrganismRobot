LOOP_INTERVAL_COGNITION = 1.0
DISTANCE_BLOCK_THRESHOLD = 20
LOOP_INTERVAL = 10.0
import os


class Settings:
    # ===== LLM =====
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    # ===== SYSTEM =====
    LOOP_INTERVAL: float = 10.0
    LOOP_INTERVAL_COGNITION: float = 1.0
    DISTANCE_BLOCK_THRESHOLD: int = 20

    # ===== ROBOT CONTROL =====
    USE_HARDWARE: bool = os.getenv("USE_HARDWARE", "true").lower() in ("true", "1", "yes")



settings = Settings()
