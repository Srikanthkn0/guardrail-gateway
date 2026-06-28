from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.providers.base import ProviderRequest
from app.providers.mock_provider import MockProvider
from app.providers.openai_provider import build_openai_provider
from app.providers.registry import complete, get_provider, list_available_providers, resolve_provider_name

client = TestClient(app)


@pytest.mark.anyio
async def test_mock_provider_deterministic():
    provider = MockProvider()
    assert provider.is_configured() is True

    result = await provider.complete(ProviderRequest(prompt="What is the capital of France?"))
    assert result.provider == "mock"
    assert result.model == "mock-v1"
    assert result.text == "Paris"
    assert result.latency_ms >= 0


@pytest.mark.anyio
async def test_mock_provider_custom_model():
    provider = MockProvider()
    result = await provider.complete(
        ProviderRequest(prompt="Summarize this.", model="mock-custom")
    )
    assert result.model == "mock-custom"
    assert "Mock summary" in result.text


def test_list_available_providers_without_keys():
    providers = {item["id"]: item for item in list_available_providers()}
    assert providers["mock"]["available"] is True
    assert providers["openai"]["available"] is bool(settings.OPENAI_API_KEY)
    assert providers["grok"]["available"] is bool(settings.XAI_API_KEY)
    assert providers["gemini"]["available"] is bool(settings.GEMINI_API_KEY)


def test_resolve_unknown_provider_raises_400():
    with pytest.raises(Exception) as exc:
        resolve_provider_name("anthropic")
    assert "Unknown provider" in exc.value.detail


def test_resolve_unconfigured_openai_raises_400(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    with pytest.raises(Exception) as exc:
        resolve_provider_name("openai")
    assert "OPENAI_API_KEY" in exc.value.detail


@pytest.mark.anyio
async def test_complete_openai_with_mocked_http(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "ok"
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello from OpenAI"}}]
    }

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("app.providers.openai_compatible.httpx.AsyncClient", return_value=mock_client):
        result = await complete("openai", "Say hello")

    assert result.provider == "openai"
    assert result.text == "Hello from OpenAI"
    assert result.model == "gpt-4o-mini"


def test_gateway_uses_mock_by_default():
    response = client.post(
        "/gateway/chat",
        json={"prompt": "What is 2 + 2?"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "mock"
    assert payload["response_text"] == "4"


@pytest.mark.anyio
async def test_complete_gemini_with_mocked_http(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "ok"
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Hello from Gemini"}]}}]
    }

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("app.providers.gemini_provider.httpx.AsyncClient", return_value=mock_client):
        result = await complete("gemini", "Say hello")

    assert result.provider == "gemini"
    assert result.text == "Hello from Gemini"
    assert result.model == "gemini-2.5-flash-lite"


def test_gateway_rejects_unconfigured_openai(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    response = client.post(
        "/gateway/chat",
        json={"prompt": "What is the capital of France?", "provider": "openai"},
    )
    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_openai_provider_not_configured_raises():
    provider = build_openai_provider()
    monkeypatched = provider
    with patch.object(monkeypatched, "_api_key", ""):
        assert monkeypatched.is_configured() is False