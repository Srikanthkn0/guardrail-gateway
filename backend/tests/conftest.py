import os

import pytest

from app import config
from app.config import settings
from app.services.ml_classifier import reload_model
from app.storage import log_store

os.environ["ML_GUARD_BACKEND"] = "sklearn"
os.environ["ML_GUARD_ENABLED"] = "true"


@pytest.fixture(scope="session", autouse=True)
def _ensure_sklearn_classifier():
    if not settings.ML_GUARD_SKLEARN_PATH.exists():
        from scripts.train_sklearn_classifier import main as train_main

        train_main()
    reload_model()


@pytest.fixture(autouse=True)
def isolated_log_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(log_store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(log_store, "DB_PATH", tmp_path / "gateway.db")
    log_store.init_db()
    yield