import re

from app.models import RuleHit, ScanPhaseResult
from app.services.decision_engine import decide_from_hits
from app.services.rules_catalog import GuardrailRule


def _match_phrase(text: str, phrase: str) -> bool:
    return phrase.lower() in text.lower()


def _match_regex(text: str, pattern: str) -> re.Match[str] | None:
    return re.search(pattern, text, flags=re.IGNORECASE)


def evaluate_rule(text: str, rule: GuardrailRule) -> RuleHit | None:
    if rule.match_type == "phrase":
        if not _match_phrase(text, rule.pattern):
            return None
        return RuleHit(
            rule_id=rule.id,
            rule_name=rule.name,
            category=rule.category,
            severity=rule.severity,
            match_type=rule.match_type,
            matched_text=rule.pattern,
            description=rule.description,
        )

    match = _match_regex(text, rule.pattern)
    if not match:
        return None
    return RuleHit(
        rule_id=rule.id,
        rule_name=rule.name,
        category=rule.category,
        severity=rule.severity,
        match_type=rule.match_type,
        matched_text=match.group(0),
        description=rule.description,
    )


def scan_text(
    text: str,
    rules: list[GuardrailRule],
    *,
    phase: str,
    empty_reason: str,
) -> ScanPhaseResult:
    normalized = text.strip()
    if not normalized:
        return ScanPhaseResult(
            phase=phase,
            decision="allow",
            hits=[],
            reasons=[empty_reason],
        )

    hits: list[RuleHit] = []
    for rule in rules:
        hit = evaluate_rule(normalized, rule)
        if hit:
            hits.append(hit)

    decision, reasons = decide_from_hits(hits)
    return ScanPhaseResult(
        phase=phase,
        decision=decision,
        hits=hits,
        reasons=reasons,
    )