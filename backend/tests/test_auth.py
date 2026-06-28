from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_health_public_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    monkeypatch.setattr(settings, "REQUIRE_API_KEY", True)
    response = client.get("/health")
    assert response.status_code == 200


def test_gateway_requires_api_key_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    monkeypatch.setattr(settings, "REQUIRE_API_KEY", True)

    blocked = client.post("/gateway/chat", json={"prompt": "Hello"})
    assert blocked.status_code == 401

    allowed = client.post(
        "/gateway/chat",
        json={"prompt": "Hello"},
        headers={"X-API-Key": "secret-key"},
    )
    assert allowed.status_code == 200


def test_logs_requires_api_key_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    monkeypatch.setattr(settings, "REQUIRE_API_KEY", True)

    response = client.get("/logs")
    assert response.status_code == 401

    response = client.get("/logs", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 200