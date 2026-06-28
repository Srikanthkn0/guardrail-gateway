from fastapi import HTTPException

from app.config import settings
from app.providers.base import (
    LLMProvider,
    ProviderNotConfiguredError,
    ProviderRequest,
    ProviderResponse,
)
from app.providers.groq_provider import build_groq_provider
from app.providers.mock_provider import mock_provider
from app.providers.openai_compatible import missing_key_message
from app.providers.openai_provider import build_openai_provider


def get_registry() -> dict[str, LLMProvider]:
    """Build registry from current settings so tests can patch env vars."""
    return {
        mock_provider.id: mock_provider,
        "openai": build_openai_provider(),
        "groq": build_groq_provider(),
    }


def get_provider(provider_id: str) -> LLMProvider | None:
    return get_registry().get(provider_id)


def list_available_providers() -> list[dict[str, str | bool]]:
    return [
        {
            "id": provider.id,
            "label": provider.label,
            "available": provider.is_configured(),
        }
        for provider in get_registry().values()
    ]


def resolve_provider_name(requested: str | None) -> str:
    provider_id = (requested or settings.DEFAULT_PROVIDER).strip().lower()
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