from typing import Literal

from pydantic import BaseModel, Field

Decision = Literal["allow", "warn", "block"]


class ProviderStatus(BaseModel):
    id: str
    label: str
    available: bool
    models: list[str] = Field(default_factory=list)
    default_model: str | None = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    default_provider: str
    effective_default_provider: str
    providers: list[ProviderStatus]


RuleSeverity = Literal["block", "warn"]


RuleScope = Literal["input", "output"]


class RuleSummary(BaseModel):
    id: str
    name: str
    category: str
    severity: RuleSeverity
    match_type: str
    description: str
    scope: RuleScope


class RulesListResponse(BaseModel):
    count: int
    rules: list[RuleSummary]


class RuleHit(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: RuleSeverity
    match_type: str
    matched_text: str
    description: str


class ScanPhaseResult(BaseModel):
    phase: str
    decision: Decision
    matched_rule_ids: list[str] = Field(default_factory=list)
    hits: list[RuleHit]
    reasons: list[str]
    ml_enabled: bool = False
    ml_loaded: bool = False
    ml_backend: str | None = None
    ml_score: float | None = None
    ml_label: str | None = None
    ml_model: str | None = None


class RuleTestRequest(BaseModel):
    text: str = Field(..., min_length=0, max_length=20000)
    output_text: str | None = Field(default=None, max_length=20000)


class RuleTestResponse(BaseModel):
    input: ScanPhaseResult
    output: ScanPhaseResult | None = None
    final_decision: Decision | None = None


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=20000)
    provider: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    request_id: str
    input_scan: ScanPhaseResult
    output_scan: ScanPhaseResult | None = None
    final_decision: Decision
    forwarded: bool
    llm_called: bool = False
    response_redacted: bool = False
    provider: str | None = None
    model: str | None = None
    response_text: str | None = None
    latency_ms: float | None = None
    reasons: list[str] = Field(default_factory=list)


class GatewayLogEntry(BaseModel):
    request_id: str
    created_at: str
    prompt_preview: str
    provider: str | None = None
    model: str | None = None
    input_decision: Decision
    output_decision: Decision | None = None
    final_decision: Decision
    forwarded: bool
    latency_ms: float | None = None
    response_redacted: bool = False
    input_hit_count: int = 0
    output_hit_count: int = 0
    reasons: list[str] = Field(default_factory=list)
    input_hits: list[RuleHit] = Field(default_factory=list)
    output_hits: list[RuleHit] = Field(default_factory=list)
    response_text: str | None = None


class LogsListResponse(BaseModel):
    count: int
    limit: int
    offset: int
    logs: list[GatewayLogEntry]


class ProviderStat(BaseModel):
    provider: str
    count: int
    avg_latency_ms: float | None = None


class GatewayStatsResponse(BaseModel):
    total_requests: int
    allow_count: int
    warn_count: int
    block_count: int
    forwarded_count: int
    block_rate: float
    warn_rate: float
    avg_latency_ms: float | None = None
    by_provider: list[ProviderStat]