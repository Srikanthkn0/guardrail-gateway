from app.models import RuleHit
from app.services.decision_engine import combine_decisions, decide_from_hits, merge_reasons


def _hit(rule_id: str, severity: str) -> RuleHit:
    return RuleHit(
        rule_id=rule_id,
        rule_name=rule_id,
        category="test",
        severity=severity,
        match_type="phrase",
        matched_text="x",
        description="test",
    )


def test_combine_decisions_block_wins():
    assert combine_decisions("allow", "warn", "block") == "block"
    assert combine_decisions("warn", "allow") == "warn"
    assert combine_decisions("allow", "allow") == "allow"


def test_merge_reasons_deduplicates():
    merged = merge_reasons(
        ["Blocked by a", "Blocked by b"],
        ["Blocked by a", "Warning from c"],
    )
    assert merged == ["Blocked by a", "Blocked by b", "Warning from c"]


def test_decide_from_hits_empty():
    decision, reasons = decide_from_hits([])
    assert decision == "allow"
    assert reasons == ["No guardrail rules matched."]


def test_decide_from_hits_block_over_warn():
    decision, reasons = decide_from_hits(
        [_hit("warn_rule", "warn"), _hit("block_rule", "block")]
    )
    assert decision == "block"
    assert len(reasons) == 1
    assert "block_rule" in reasons[0]