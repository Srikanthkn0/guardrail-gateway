import uuid

from app.models import ChatResponse
from app.providers.router import complete, resolve_provider_name
from app.services.decision_engine import combine_decisions, merge_reasons
from app.services.input_scanner import scan_input
from app.services.output_scanner import scan_output
from app.storage.log_store import record_gateway_request


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
            reasons=input_scan.reasons,
        )
        record_gateway_request(prompt, response)
        return response

    provider_name = resolve_provider_name(provider)
    completion = await complete(provider_name, prompt, model=model)
    output_scan = scan_output(completion.text)
    final_decision = combine_decisions(input_scan.decision, output_scan.decision)
    reasons = merge_reasons(input_scan.reasons, output_scan.reasons)

    response_text = completion.text
    if output_scan.decision == "block":
        response_text = None

    response = ChatResponse(
        request_id=request_id,
        input_scan=input_scan,
        output_scan=output_scan,
        final_decision=final_decision,
        forwarded=True,
        provider=completion.provider,
        model=completion.model,
        response_text=response_text,
        latency_ms=completion.latency_ms,
        reasons=reasons,
    )
    record_gateway_request(prompt, response)
    return response