from fastapi import APIRouter, HTTPException

from app.models import RuleSummary, RuleTestRequest, RuleTestResponse, RulesListResponse
from app.services.guardrail_engine import evaluate_both, evaluate_input
from app.services.rules_catalog import get_rule, list_rules

router = APIRouter()


@router.get("/rules", response_model=RulesListResponse)
async def get_rules():
    rules = [
        RuleSummary(
            id=rule.id,
            name=rule.name,
            category=rule.category,
            severity=rule.severity,
            match_type=rule.match_type,
            description=rule.description,
            scope=rule.scope,
        )
        for rule in list_rules()
    ]
    return RulesListResponse(count=len(rules), rules=rules)


@router.get("/rules/{rule_id}", response_model=RuleSummary)
async def get_rule_detail(rule_id: str):
    rule = get_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found.")
    return RuleSummary(
        id=rule.id,
        name=rule.name,
        category=rule.category,
        severity=rule.severity,
        match_type=rule.match_type,
        description=rule.description,
        scope=rule.scope,
    )


@router.post("/rules/test", response_model=RuleTestResponse)
async def test_rules(payload: RuleTestRequest):
    if payload.output_text is not None:
        input_result, output_result, final_decision = evaluate_both(
            payload.text,
            payload.output_text,
        )
    else:
        input_result = evaluate_input(payload.text)
        output_result = None
        final_decision = input_result.decision

    return RuleTestResponse(
        input=input_result,
        output=output_result,
        final_decision=final_decision,
    )