from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_security_headers_present():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "X-Request-ID" in response.headers


def test_production_flag(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "production")
    assert settings.is_production is True


def test_readiness_endpoint():
    response = client.get("/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ready", "degraded"}
    assert "checks" in payload