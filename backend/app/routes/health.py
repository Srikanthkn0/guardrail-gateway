from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse, ProviderStatus
from app.providers.router import list_available_providers

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    providers = [
        ProviderStatus(
            id=item["id"],
            label=item["label"],
            available=item["available"],
        )
        for item in list_available_providers()
    ]
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        default_provider=settings.DEFAULT_PROVIDER,
        providers=providers,
    )