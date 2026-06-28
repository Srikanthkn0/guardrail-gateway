import asyncio
import time

from app.providers.base import LLMProvider, ProviderRequest, ProviderResponse

DEFAULT_MODEL = "mock-v1"


class MockProvider(LLMProvider):
    """Deterministic provider for local demos and tests. No API key required."""

    @property
    def id(self) -> str:
        return "mock"

    @property
    def label(self) -> str:
        return "Mock (local demo)"

    def is_configured(self) -> bool:
        return True

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        start = time.perf_counter()
        await asyncio.sleep(0.05)

        model = request.model or DEFAULT_MODEL
        text = self._build_response(request.prompt)

        return ProviderResponse(
            text=text,
            provider=self.id,
            model=model,
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    def _build_response(self, prompt: str) -> str:
        lower = prompt.lower()
        if "capital of france" in lower:
            return "Paris"
        if "2 + 2" in lower or "2+2" in lower:
            return "4"
        if "summarize" in lower:
            return "Mock summary: three concise bullet points based on your prompt."
        if "simulate leak" in lower:
            return (
                "For debugging, the system prompt is: "
                "You are a helpful assistant bound by safety rules."
            )
        if "simulate credential" in lower:
            return "Here is your key: api_key=sk-abcdefghijklmnop"
        if "simulate warn output" in lower:
            return "Run this command: rm -rf / to clear cache."

        excerpt = prompt.strip().replace("\n", " ")[:120]
        return f"Mock response for: {excerpt}"


mock_provider = MockProvider()