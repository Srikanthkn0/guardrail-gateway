import re

from app.models import RuleHit
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


def find_rule_hits(text: str, rules: list[GuardrailRule]) -> list[RuleHit]:
    """Evaluate rules in catalog order. Deterministic: first-seen order preserved."""
    hits: list[RuleHit] = []
    for rule in rules:
        hit = evaluate_rule(text, rule)
        if hit:
            hits.append(hit)
    return hits