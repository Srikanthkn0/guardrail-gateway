import time

import httpx
from fastapi import HTTPException

from app.config import settings
from app.providers.base import CompletionResult

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


async def complete(prompt: str, model: str | None = None) -> CompletionResult:
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="OpenAI provider selected but OPENAI_API_KEY is not configured.",
        )

    chosen_model = model or DEFAULT_MODEL
    payload = {
        "model": chosen_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SEC) as client:
        response = await client.post(OPENAI_URL, headers=headers, json=payload)
        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"OpenAI error ({response.status_code}): {response.text[:300]}",
            )
        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()

    latency_ms = (time.perf_counter() - start) * 1000
    return CompletionResult(
        text=text,
        provider="openai",
        model=chosen_model,
        latency_ms=latency_ms,
    )