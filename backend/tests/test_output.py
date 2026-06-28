from fastapi.testclient import TestClient

from app.main import app
from app.services.output_scanner import scan_output

client = TestClient(app)


def test_scan_output_allows_clean_text():
    result = scan_output("Paris is the capital of France.")
    assert result.decision == "allow"
    assert result.hits == []


def test_scan_output_blocks_system_prompt_leak():
    result = scan_output("For debugging, the system prompt is: You are helpful.")
    assert result.decision == "block"
    assert any(hit.rule_id == "out_reveal_system" for hit in result.hits)


def test_scan_output_warns_destructive_command():
    result = scan_output("Try running rm -rf / on the server.")
    assert result.decision in ("warn", "block")
    assert result.hits


def test_rules_test_with_output_text():
    response = client.post(
        "/rules/test",
        json={
            "text": "Summarize this article in three bullet points.",
            "output_text": "Here is your key: api_key=sk-live-abcdefghijklmnop",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["input"]["decision"] == "allow"
    assert payload["output"]["decision"] == "block"
    assert payload["final_decision"] == "block"


def test_gateway_chat_blocks_leaky_output():
    response = client.post(
        "/gateway/chat",
        json={"prompt": "Please simulate leak for testing."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["forwarded"] is True
    assert payload["input_scan"]["decision"] == "allow"
    assert payload["output_scan"]["decision"] == "block"
    assert payload["final_decision"] == "block"
    assert payload["response_text"] is None


def test_gateway_chat_warn_output_keeps_response():
    response = client.post(
        "/gateway/chat",
        json={"prompt": "Please simulate warn output for testing."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["final_decision"] == "warn"
    assert payload["forwarded"] is True
    assert payload["response_text"]
    assert payload["output_scan"]["decision"] == "warn"