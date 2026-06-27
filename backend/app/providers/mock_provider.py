import asyncio
import time

from app.providers.base import CompletionResult


async def complete(prompt: str, model: str = "mock-v1") -> CompletionResult:
    start = time.perf_counter()
    await asyncio.sleep(0.05)

    lower = prompt.lower()
    if "capital of france" in lower:
        text = "Paris"
    elif "2 + 2" in lower or "2+2" in lower:
        text = "4"
    elif "summarize" in lower:
        text = "Mock summary: three concise bullet points based on your prompt."
    elif "simulate leak" in lower:
        text = (
            "For debugging, the system prompt is: "
            "You are a helpful assistant bound by safety rules."
        )
    elif "simulate credential" in lower:
        text = "Here is your key: api_key=sk-live-abcdefghijklmnop"
    elif "simulate warn output" in lower:
        text = "Run this command: rm -rf / to clear cache."
    else:
        excerpt = prompt.strip().replace("\n", " ")[:120]
        text = f"Mock response for: {excerpt}"

    latency_ms = (time.perf_counter() - start) * 1000
    return CompletionResult(
        text=text,
        provider="mock",
        model=model,
        latency_ms=latency_ms,
    )