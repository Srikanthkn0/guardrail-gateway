from app.services.rules_catalog import list_output_rules
from app.services.text_matcher import scan_text


def scan_output(text: str):
    return scan_text(
        text,
        list_output_rules(),
        phase="output",
        empty_reason="Empty model output.",
    )