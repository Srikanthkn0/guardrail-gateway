from fastapi import APIRouter, HTTPException

from app.models import RuleSummary, RuleTestRequest, RuleTestResponse, RulesListResponse
from app.services.decision_engine import combine_decisions
from app.services.input_scanner import scan_input
from app.services.output_scanner import scan_output
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
    input_result = scan_input(payload.text)
    output_result = None
    final_decision = input_result.decision

    if payload.output_text is not None:
        output_result = scan_output(payload.output_text)
        final_decision = combine_decisions(input_result.decision, output_result.decision)

    return RuleTestResponse(
        input=input_result,
        output=output_result,
        final_decision=final_decision,
    )