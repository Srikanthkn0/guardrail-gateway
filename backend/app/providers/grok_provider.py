from app.config import settings
from app.providers.openai_compatible import OpenAICompatibleProvider

GROK_BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-3-mini"


def build_grok_provider() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        provider_id="grok",
        label="Grok (xAI)",
        api_key=settings.XAI_API_KEY,
        base_url=GROK_BASE_URL,
        default_model=DEFAULT_MODEL,
    )