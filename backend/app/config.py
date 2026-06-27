import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

_data_dir = os.getenv("DATA_DIR", "")
DATA_DIR = Path(_data_dir) if _data_dir else BASE_DIR / "data"


def _parse_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Guardrail Gateway")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    FRONTEND_ORIGINS: list[str] = _parse_origins(
        os.getenv(
            "FRONTEND_ORIGINS",
            os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        )
    )
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "mock")
    LLM_TIMEOUT_SEC: float = float(os.getenv("LLM_TIMEOUT_SEC", "60"))

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


settings = Settings()
DATA_DIR.mkdir(parents=True, exist_ok=True)