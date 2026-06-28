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
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "") or os.getenv("GROK_API_KEY", "")
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "auto")
    LLM_TIMEOUT_SEC: float = float(os.getenv("LLM_TIMEOUT_SEC", "60"))
    ML_GUARD_ENABLED: bool = os.getenv("ML_GUARD_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    ML_GUARD_BACKEND: str = os.getenv("ML_GUARD_BACKEND", "auto")
    ML_GUARD_MODEL: str = os.getenv(
        "ML_GUARD_MODEL", "fmops/distilbert-prompt-injection"
    )
    ML_GUARD_GROK_MODEL: str = os.getenv("ML_GUARD_GROK_MODEL", "grok-3-mini")
    ML_GUARD_BLOCK_THRESHOLD: float = float(os.getenv("ML_GUARD_BLOCK_THRESHOLD", "0.85"))
    ML_GUARD_WARN_THRESHOLD: float = float(os.getenv("ML_GUARD_WARN_THRESHOLD", "0.65"))
    ML_GUARD_GROK_BLOCK_THRESHOLD: float = float(
        os.getenv("ML_GUARD_GROK_BLOCK_THRESHOLD", "0.75")
    )
    ML_GUARD_GROK_WARN_THRESHOLD: float = float(
        os.getenv("ML_GUARD_GROK_WARN_THRESHOLD", "0.55")
    )
    ML_GUARD_SKLEARN_BLOCK_THRESHOLD: float = float(
        os.getenv("ML_GUARD_SKLEARN_BLOCK_THRESHOLD", "0.58")
    )
    ML_GUARD_MAX_LENGTH: int = int(os.getenv("ML_GUARD_MAX_LENGTH", "512"))
    ML_GUARD_SKLEARN_PATH: Path = Path(
        os.getenv(
            "ML_GUARD_SKLEARN_PATH",
            str(BASE_DIR / "data" / "models" / "injection_classifier.joblib"),
        )
    )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


settings = Settings()
DATA_DIR.mkdir(parents=True, exist_ok=True)