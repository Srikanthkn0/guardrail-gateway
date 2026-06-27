from fastapi import HTTPException

from app.config import settings
from app.providers import groq_provider, mock_provider, openai_provider
from app.providers.base import CompletionResult

PROVIDER_LABELS = {
    "mock": "Mock (local demo)",
    "openai": "OpenAI",
    "groq": "Groq",
}


def list_available_providers() -> list[dict[str, str | bool]]:
    providers = [
        {"id": "mock", "label": PROVIDER_LABELS["mock"], "available": True},
        {
            "id": "openai",
            "label": PROVIDER_LABELS["openai"],
            "available": bool(settings.OPENAI_API_KEY),
        },
        {
            "id": "groq",
            "label": PROVIDER_LABELS["groq"],
            "available": bool(settings.GROQ_API_KEY),
        },
    ]
    return providers


def resolve_provider_name(requested: str | None) -> str:
    provider = (requested or settings.DEFAULT_PROVIDER).strip().lower()
    if provider not in PROVIDER_LABELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{provider}'. Use mock, openai, or groq.",
        )

    available = {item["id"]: item["available"] for item in list_available_providers()}
    if not available.get(provider):
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider}' is not configured on this server.",
        )
    return provider


async def complete(
    provider: str,
    prompt: str,
    model: str | None = None,
) -> CompletionResult:
    if provider == "mock":
        return await mock_provider.complete(prompt, model=model or "mock-v1")
    if provider == "openai":
        return await openai_provider.complete(prompt, model=model)
    if provider == "groq":
        return await groq_provider.complete(prompt, model=model)
    raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'.")