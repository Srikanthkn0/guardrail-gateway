from dataclasses import dataclass
from typing import Literal

RuleScope = Literal["input", "output"]


@dataclass(frozen=True)
class GuardrailRule:
    id: str
    name: str
    category: str
    severity: Literal["block", "warn"]
    match_type: Literal["phrase", "regex"]
    pattern: str
    description: str
    scope: RuleScope = "input"