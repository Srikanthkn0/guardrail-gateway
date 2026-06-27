import pytest

from app import config
from app.storage import log_store


@pytest.fixture(autouse=True)
def isolated_log_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(log_store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(log_store, "DB_PATH", tmp_path / "gateway.db")
    log_store.init_db()
    yield