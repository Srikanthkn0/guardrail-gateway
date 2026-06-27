from dataclasses import dataclass


@dataclass
class CompletionResult:
    text: str
    provider: str
    model: str
    latency_ms: float