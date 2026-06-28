import os

# Must run before app.config loads settings from .env
os.environ["ML_GUARD_BACKEND"] = "sklearn"
os.environ["ML_GUARD_ENABLED"] = "true"
os.environ["OPENAI_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["XAI_API_KEY"] = ""
os.environ["GROK_API_KEY"] = ""
os.environ["DEFAULT_PROVIDER"] = "mock"
os.environ["API_KEY"] = ""
os.environ["REQUIRE_API_KEY"] = "false"
os.environ["APP_ENV"] = "development"

import pytest

from app import config
from app.config import settings
from app.services.ml_classifier import reload_model
from app.storage import log_store


@pytest.fixture(scope="session", autouse=True)
def _ensure_sklearn_classifier():
    if not settings.ML_GUARD_SKLEARN_PATH.exists():
        from scripts.train_sklearn_classifier import main as train_main

        train_main()
    reload_model()


@pytest.fixture(autouse=True)
def reset_ml_classifier():
    reload_model()
    yield
    reload_model()


@pytest.fixture(autouse=True)
def isolated_log_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(log_store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(log_store, "DB_PATH", tmp_path / "gateway.db")
    log_store.init_db()
    yield