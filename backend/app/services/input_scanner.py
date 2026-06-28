from app.services.guardrail_engine import evaluate_input


def scan_input(text: str):
    return evaluate_input(text)