import uuid

from fastapi import HTTPException

from app.config import settings
from app.models import ChatResponse
from app.providers.registry import get_provider
from app.providers.router import complete, resolve_provider_name
from app.services.decision_engine import combine_decisions, merge_reasons
from app.services.input_scanner import scan_input
from app.services.output_scanner import scan_output
from app.storage.log_store import record_gateway_request

FALLBACK_CHAIN: dict[str, list[str]] = {
    "grok": ["gemini", "openai"],
    "gemini": ["openai"],
}


def _fallback_providers(provider_name: str) -> list[str]:
    candidates = FALLBACK_CHAIN.get(provider_name, [])
    available = []
    for provider_id in candidates:
        provider = get_provider(provider_id)
        if provider and provider.is_configured():
            available.append(provider_id)
    return available


async def _call_provider(provider_name: str, prompt: str, model: str | None):
    try:
        return await complete(provider_name, prompt, model=model)
    except HTTPException as exc:
        if exc.status_code != 502:
            raise
        for fallback_id in _fallback_providers(provider_name):
            try:
                return await complete(fallback_id, prompt, model=None)
            except HTTPException:
                continue
        raise


async def handle_chat(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
) -> ChatResponse:
    request_id = str(uuid.uuid4())
    input_scan = scan_input(prompt)

    if input_scan.decision == "block":
        response = ChatResponse(
            request_id=request_id,
            input_scan=input_scan,
            output_scan=None,
            final_decision="block",
            forwarded=False,
            llm_called=False,
            response_redacted=False,
            reasons=input_scan.reasons,
        )
        record_gateway_request(prompt, response)
        return response

    provider_name = resolve_provider_name(provider)
    completion = await _call_provider(provider_name, prompt, model=model)
    output_scan = scan_output(completion.text)
    final_decision = combine_decisions(input_scan.decision, output_scan.decision)
    reasons = merge_reasons(input_scan.reasons, output_scan.reasons)

    response_redacted = output_scan.decision == "block"
    response_text = None if response_redacted else completion.text

    response = ChatResponse(
        request_id=request_id,
        input_scan=input_scan,
        output_scan=output_scan,
        final_decision=final_decision,
        forwarded=True,
        llm_called=True,
        response_redacted=response_redacted,
        provider=completion.provider,
        model=completion.model,
        response_text=response_text,
        latency_ms=completion.latency_ms,
        reasons=reasons,
    )
    record_gateway_request(prompt, response)
    return response