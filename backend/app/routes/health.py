from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse, ProviderStatus
from app.providers.registry import effective_default_provider
from app.providers.router import list_available_providers
from app.services.ml_classifier import classifier_status

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    providers = [
        ProviderStatus(
            id=item["id"],
            label=item["label"],
            available=item["available"],
            models=item.get("models", []),
            default_model=item.get("default_model"),
        )
        for item in list_available_providers()
    ]
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        default_provider=settings.DEFAULT_PROVIDER,
        effective_default_provider=effective_default_provider(),
        providers=providers,
    )


@router.get("/health/ml")
async def ml_health():
    return classifier_status()