import json
from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.services.input_scanner import scan_input
from app.services.ml_classifier import ML_RULE_ID, predict_injection, reload_model
from tests.fixtures.adversarial_cases import INPUT_ML_SHOULD_BLOCK


def test_grok_failure_falls_back_to_sklearn(monkeypatch):
    monkeypatch.setattr(settings, "XAI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "ML_GUARD_BACKEND", "auto")
    reload_model()

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "permission denied"

    with patch("app.services.grok_classifier.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        pred = predict_injection(INPUT_ML_SHOULD_BLOCK[0])

    assert pred.loaded is True
    assert pred.backend == "sklearn"
    assert pred.fallback_used is True


def test_scan_still_blocks_paraphrase_when_grok_fails(monkeypatch):
    monkeypatch.setattr(settings, "XAI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "ML_GUARD_BACKEND", "auto")
    reload_model()

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "permission denied"

    with patch("app.services.grok_classifier.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        result = scan_input(INPUT_ML_SHOULD_BLOCK[0])

    assert result.decision == "block"
    assert ML_RULE_ID in result.matched_rule_ids
    assert result.ml_backend == "sklearn"


@pytest.mark.parametrize("text", INPUT_ML_SHOULD_BLOCK)
def test_sklearn_blocks_paraphrases_after_grok_error(text: str, monkeypatch):
    monkeypatch.setattr(settings, "XAI_API_KEY", "test-key")
    reload_model()

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "error"

    with patch("app.services.grok_classifier.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.post.return_value = mock_response
        result = scan_input(text)

    assert result.decision == "block", text