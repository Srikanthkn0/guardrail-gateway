from app.services.guardrail_engine import evaluate_output


def scan_output(text: str):
    return evaluate_output(text)