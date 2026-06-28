from fastapi import HTTPException

from app.config import settings
from app.providers.base import (
    LLMProvider,
    ProviderNotConfiguredError,
    ProviderRequest,
    ProviderResponse,
)
from app.providers.grok_provider import build_grok_provider
from app.providers.mock_provider import mock_provider
from app.providers.openai_compatible import missing_key_message
from app.providers.openai_provider import build_openai_provider

PROVIDER_MODELS: dict[str, list[str]] = {
    "mock": ["mock-v1"],
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
    "grok": ["grok-3-mini", "grok-3", "grok-4.3"],
}


def get_registry() -> dict[str, LLMProvider]:
    """Build registry from current settings so tests can patch env vars."""
    return {
        mock_provider.id: mock_provider,
        "openai": build_openai_provider(),
        "grok": build_grok_provider(),
    }


def get_provider(provider_id: str) -> LLMProvider | None:
    return get_registry().get(provider_id)


def effective_default_provider() -> str:
    """Pick the best configured provider: explicit env, then auto-detect keys."""
    requested = settings.DEFAULT_PROVIDER.strip().lower()

    if requested not in {"", "auto"}:
        provider = get_provider(requested)
        if provider and provider.is_configured():
            return requested

    if settings.XAI_API_KEY.strip():
        return "grok"
    if settings.OPENAI_API_KEY.strip():
        return "openai"
    return "mock"


def list_available_providers() -> list[dict[str, str | bool | list[str]]]:
    return [
        {
            "id": provider.id,
            "label": provider.label,
            "available": provider.is_configured(),
            "models": PROVIDER_MODELS.get(provider.id, []),
            "default_model": PROVIDER_MODELS.get(provider.id, [None])[0],
        }
        for provider in get_registry().values()
    ]


def resolve_provider_name(requested: str | None) -> str:
    provider_id = (requested or effective_default_provider()).strip().lower()
    provider = get_provider(provider_id)

    if provider is None:
        known = ", ".join(sorted(get_registry()))
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{provider_id}'. Use {known}.",
        )

    if not provider.is_configured():
        raise HTTPException(
            status_code=400,
            detail=missing_key_message(provider_id),
        )

    return provider_id


async def complete(
    provider_id: str,
    prompt: str,
    model: str | None = None,
) -> ProviderResponse:
    provider = get_provider(provider_id)
    if provider is None:
        raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider_id}'.")

    try:
        return await provider.complete(ProviderRequest(prompt=prompt, model=model))
    except ProviderNotConfiguredError as exc:
        raise HTTPException(status_code=400, detail=exc.detail) from exc