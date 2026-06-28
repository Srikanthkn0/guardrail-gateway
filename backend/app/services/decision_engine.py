from dataclasses import dataclass
from typing import Literal

from app.models import RuleHit

Decision = Literal["allow", "warn", "block"]

# block > warn > allow — fixed priority for deterministic MVP decisions
_DECISION_RANK: dict[Decision, int] = {"allow": 0, "warn": 1, "block": 2}


@dataclass(frozen=True)
class DecisionResult:
    """Outcome of evaluating text against a rule set."""

    decision: Decision
    matched_rule_ids: list[str]
    reasons: list[str]
    hits: list[RuleHit]

    @property
    def has_matches(self) -> bool:
        return bool(self.matched_rule_ids)


def classify_hits(hits: list[RuleHit]) -> DecisionResult:
    """
    Map rule hits to allow / warn / block.

    - No hits -> allow
    - Any block-severity hit -> block (all block hits reported)
    - Else any warn-severity hit -> warn (all warn hits reported)
    """
    if not hits:
        return DecisionResult(
            decision="allow",
            matched_rule_ids=[],
            reasons=["No guardrail rules matched."],
            hits=[],
        )

    block_hits = [hit for hit in hits if hit.severity == "block"]
    if block_hits:
        return DecisionResult(
            decision="block",
            matched_rule_ids=[hit.rule_id for hit in block_hits],
            reasons=[
                f"Blocked by {hit.rule_id}: {hit.rule_name}" for hit in block_hits
            ],
            hits=hits,
        )

    warn_hits = [hit for hit in hits if hit.severity == "warn"]
    return DecisionResult(
        decision="warn",
        matched_rule_ids=[hit.rule_id for hit in warn_hits],
        reasons=[f"Warning from {hit.rule_id}: {hit.rule_name}" for hit in warn_hits],
        hits=hits,
    )


def combine_decisions(*decisions: Decision) -> Decision:
    """Pick the strictest decision across scan phases."""
    return max(decisions, key=lambda decision: _DECISION_RANK[decision])


def combine_results(*results: DecisionResult) -> DecisionResult:
    """Merge multiple phase results into one final decision."""
    if not results:
        return classify_hits([])

    decision = combine_decisions(*(result.decision for result in results))
    matched_rule_ids: list[str] = []
    reasons: list[str] = []
    hits: list[RuleHit] = []

    for result in results:
        for rule_id in result.matched_rule_ids:
            if rule_id not in matched_rule_ids:
                matched_rule_ids.append(rule_id)
        reasons = merge_reasons(reasons, result.reasons)
        hits.extend(result.hits)

    return DecisionResult(
        decision=decision,
        matched_rule_ids=matched_rule_ids,
        reasons=reasons,
        hits=hits,
    )


def merge_reasons(*reason_groups: list[str]) -> list[str]:
    """Deduplicate reason strings while preserving order."""
    merged: list[str] = []
    seen: set[str] = set()
    for reasons in reason_groups:
        for reason in reasons:
            if reason not in seen:
                seen.add(reason)
                merged.append(reason)
    return merged


# Backward-compatible helpers used by scanners and routes
def decide_from_hits(hits: list[RuleHit]) -> tuple[Decision, list[str]]:
    result = classify_hits(hits)
    return result.decision, result.reasons