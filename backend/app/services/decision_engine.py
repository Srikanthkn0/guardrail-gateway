from typing import Literal

from app.models import RuleHit

Decision = Literal["allow", "warn", "block"]

_DECISION_RANK = {"allow": 0, "warn": 1, "block": 2}


def combine_decisions(*decisions: Decision) -> Decision:
    return max(decisions, key=lambda decision: _DECISION_RANK[decision])


def merge_reasons(*reason_groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for reasons in reason_groups:
        for reason in reasons:
            if reason not in seen:
                seen.add(reason)
                merged.append(reason)
    return merged


def decide_from_hits(hits: list[RuleHit]) -> tuple[Decision, list[str]]:
    if not hits:
        return "allow", ["No guardrail rules matched."]

    block_hits = [hit for hit in hits if hit.severity == "block"]
    warn_hits = [hit for hit in hits if hit.severity == "warn"]

    if block_hits:
        reasons = [f"Blocked by {hit.rule_id}: {hit.rule_name}" for hit in block_hits]
        return "block", reasons

    reasons = [f"Warning from {hit.rule_id}: {hit.rule_name}" for hit in warn_hits]
    return "warn", reasons