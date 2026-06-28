"""
Unified guardrail evaluation entry point.

Rules from rules_catalog + text_matcher. Input also runs ML injection classifier.
"""

from app.models import Decision, RuleHit, ScanPhaseResult
from app.services.decision_engine import DecisionResult, classify_hits, combine_decisions, combine_results
from app.services.ml_classifier import ML_RULE_ID, ml_decision, predict_injection
from app.services.rules_catalog import GuardrailRule, list_input_rules, list_output_rules
from app.services.text_matcher import find_rule_hits


def _to_scan_phase(phase: str, result: DecisionResult) -> ScanPhaseResult:
    return ScanPhaseResult(
        phase=phase,
        decision=result.decision,
        matched_rule_ids=result.matched_rule_ids,
        hits=result.hits,
        reasons=result.reasons,
    )


def _evaluate(
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
            matched_rule_ids=[],
            hits=[],
            reasons=[empty_reason],
        )

    hits = find_rule_hits(normalized, rules)
    return _to_scan_phase(phase, classify_hits(hits))


def _apply_ml_to_input(phase: ScanPhaseResult, text: str) -> ScanPhaseResult:
    ml = predict_injection(text)
    decision = phase.decision
    matched_rule_ids = list(phase.matched_rule_ids)
    reasons = list(phase.reasons)
    hits = list(phase.hits)

    ml_hit = ml_decision(ml.injection_score, ml.backend) if ml.loaded else None
    if ml_hit == "block":
        decision = combine_decisions(decision, "block")
        if ML_RULE_ID not in matched_rule_ids:
            matched_rule_ids.append(ML_RULE_ID)
        reason = (
            f"ML classifier blocked ({ml.injection_score:.1%} injection, {ml.backend})"
        )
        if reason not in reasons:
            reasons.append(reason)
        hits.append(
            RuleHit(
                rule_id=ML_RULE_ID,
                rule_name="ML injection classifier",
                category="ml_classifier",
                severity="block",
                match_type="model",
                matched_text=text[:120],
                description=f"Hugging Face / sklearn prompt-injection model ({ml.model_name})",
            )
        )
    elif ml_hit == "warn":
        decision = combine_decisions(decision, "warn")
        reason = f"ML classifier warning ({ml.injection_score:.1%} injection)"
        if reason not in reasons:
            reasons.append(reason)

    return ScanPhaseResult(
        phase=phase.phase,
        decision=decision,
        matched_rule_ids=matched_rule_ids,
        hits=hits,
        reasons=reasons,
        ml_enabled=ml.enabled,
        ml_loaded=ml.loaded,
        ml_backend=ml.backend if ml.loaded else None,
        ml_score=ml.injection_score if ml.loaded else None,
        ml_label=ml.label if ml.loaded else None,
        ml_model=ml.model_name if ml.loaded else None,
    )


def evaluate_input(text: str) -> ScanPhaseResult:
    phase = _evaluate(
        text,
        list_input_rules(),
        phase="input",
        empty_reason="Empty input.",
    )
    return _apply_ml_to_input(phase, text)


def evaluate_output(text: str) -> ScanPhaseResult:
    return _evaluate(
        text,
        list_output_rules(),
        phase="output",
        empty_reason="Empty model output.",
    )


def evaluate_both(
    input_text: str,
    output_text: str,
) -> tuple[ScanPhaseResult, ScanPhaseResult, Decision]:
    input_result = evaluate_input(input_text)
    output_result = evaluate_output(output_text)
    combined = combine_results(
        DecisionResult(
            decision=input_result.decision,
            matched_rule_ids=input_result.matched_rule_ids,
            reasons=input_result.reasons,
            hits=input_result.hits,
        ),
        DecisionResult(
            decision=output_result.decision,
            matched_rule_ids=output_result.matched_rule_ids,
            reasons=output_result.reasons,
            hits=output_result.hits,
        ),
    )
    return input_result, output_result, combined.decision