from app.services.rules_catalog import list_input_rules
from app.services.text_matcher import scan_text


def scan_input(text: str):
    return scan_text(
        text,
        list_input_rules(),
        phase="input",
        empty_reason="Empty input.",
    )