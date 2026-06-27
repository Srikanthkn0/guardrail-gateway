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


# Phrase matches are case-insensitive substring checks.
# Regex patterns use standard Python re with IGNORECASE.

INPUT_RULES: list[GuardrailRule] = [
    GuardrailRule(
        id="inj_ignore_prev",
        name="Ignore previous instructions",
        category="prompt_injection",
        severity="block",
        match_type="phrase",
        pattern="ignore previous instructions",
        description="Direct attempt to override prior system or policy instructions.",
    ),
    GuardrailRule(
        id="inj_reveal_system",
        name="Reveal system prompt",
        category="prompt_injection",
        severity="block",
        match_type="phrase",
        pattern="reveal system prompt",
        description="Attempts to extract hidden system instructions.",
    ),
    GuardrailRule(
        id="inj_show_hidden",
        name="Show hidden prompt",
        category="prompt_injection",
        severity="block",
        match_type="phrase",
        pattern="show hidden prompt",
        description="Attempts to expose concealed prompt content.",
    ),
    GuardrailRule(
        id="inj_bypass_safety",
        name="Bypass safety",
        category="policy_bypass",
        severity="block",
        match_type="phrase",
        pattern="bypass safety",
        description="Explicit request to disable safety controls.",
    ),
    GuardrailRule(
        id="inj_dev_mode",
        name="Developer mode jailbreak",
        category="jailbreak",
        severity="block",
        match_type="phrase",
        pattern="act as developer mode",
        description="Common jailbreak framing to lift model restrictions.",
    ),
    GuardrailRule(
        id="inj_print_secrets",
        name="Print secrets",
        category="credential_request",
        severity="block",
        match_type="phrase",
        pattern="print secrets",
        description="Requests exposure of secrets or credentials.",
    ),
    GuardrailRule(
        id="inj_disregard",
        name="Disregard instructions",
        category="prompt_injection",
        severity="block",
        match_type="phrase",
        pattern="disregard your instructions",
        description="Attempts to nullify standing instructions.",
    ),
    GuardrailRule(
        id="inj_dan",
        name="DAN jailbreak marker",
        category="jailbreak",
        severity="block",
        match_type="phrase",
        pattern="do anything now",
        description="Known jailbreak acronym expansion phrasing.",
    ),
    GuardrailRule(
        id="warn_pretend",
        name="Pretend persona shift",
        category="jailbreak",
        severity="warn",
        match_type="phrase",
        pattern="pretend you are",
        description="Persona swap that can weaken policy adherence.",
    ),
    GuardrailRule(
        id="warn_no_restrictions",
        name="No restrictions",
        category="policy_bypass",
        severity="warn",
        match_type="phrase",
        pattern="no restrictions",
        description="Language suggesting policy should not apply.",
    ),
    GuardrailRule(
        id="warn_override_rules",
        name="Override rules",
        category="policy_bypass",
        severity="warn",
        match_type="phrase",
        pattern="override rules",
        description="Ambiguous policy override wording.",
    ),
    GuardrailRule(
        id="warn_without_filters",
        name="Without filters",
        category="policy_bypass",
        severity="warn",
        match_type="phrase",
        pattern="without filters",
        description="Requests output without normal safeguards.",
    ),
    GuardrailRule(
        id="cred_api_key",
        name="API key assignment",
        category="credential_request",
        severity="block",
        match_type="regex",
        pattern=r"(?i)\bapi[_ -]?key\s*[:=]\s*\S+",
        description="Prompt includes an API key assignment pattern.",
    ),
    GuardrailRule(
        id="cred_token_like",
        name="Token or secret assignment",
        category="credential_request",
        severity="block",
        match_type="regex",
        pattern=r"(?i)\b(password|secret|token)\s*[:=]\s*\S+",
        description="Prompt includes credential-like assignment text.",
    ),
    GuardrailRule(
        id="cred_sk_live",
        name="Stripe-style secret key",
        category="credential_request",
        severity="block",
        match_type="regex",
        pattern=r"sk-[A-Za-z0-9]{10,}",
        description="Token-like secret key marker in prompt text.",
    ),
]

OUTPUT_RULES: list[GuardrailRule] = [
    GuardrailRule(
        id="out_reveal_system",
        name="System prompt leak",
        category="data_leak",
        severity="block",
        match_type="phrase",
        pattern="system prompt is",
        description="Model output appears to expose system instructions.",
        scope="output",
    ),
    GuardrailRule(
        id="out_hidden_instructions",
        name="Hidden instructions leak",
        category="data_leak",
        severity="block",
        match_type="phrase",
        pattern="hidden instructions are",
        description="Model output appears to reveal concealed instructions.",
        scope="output",
    ),
    GuardrailRule(
        id="out_api_key",
        name="API key in output",
        category="credential_leak",
        severity="block",
        match_type="regex",
        pattern=r"(?i)\bapi[_ -]?key\s*[:=]\s*\S+",
        description="Model output includes an API key assignment.",
        scope="output",
    ),
    GuardrailRule(
        id="out_token_like",
        name="Token or secret in output",
        category="credential_leak",
        severity="block",
        match_type="regex",
        pattern=r"(?i)\b(password|secret|token)\s*[:=]\s*\S+",
        description="Model output includes credential-like assignment text.",
        scope="output",
    ),
    GuardrailRule(
        id="out_sk_live",
        name="Stripe-style secret key in output",
        category="credential_leak",
        severity="block",
        match_type="regex",
        pattern=r"sk-[A-Za-z0-9]{10,}",
        description="Token-like secret key marker in model output.",
        scope="output",
    ),
    GuardrailRule(
        id="out_destructive_cmd",
        name="Destructive shell command",
        category="unsafe_content",
        severity="warn",
        match_type="regex",
        pattern=r"(?i)\brm\s+-rf\b",
        description="Output suggests a destructive filesystem command.",
        scope="output",
    ),
    GuardrailRule(
        id="out_disable_safety",
        name="Disable safety in output",
        category="policy_bypass",
        severity="warn",
        match_type="phrase",
        pattern="disable safety",
        description="Output encourages turning off safety controls.",
        scope="output",
    ),
]

RULES: list[GuardrailRule] = INPUT_RULES + OUTPUT_RULES


def list_rules() -> list[GuardrailRule]:
    return list(RULES)


def list_input_rules() -> list[GuardrailRule]:
    return list(INPUT_RULES)


def list_output_rules() -> list[GuardrailRule]:
    return list(OUTPUT_RULES)


def get_rule(rule_id: str) -> GuardrailRule | None:
    return next((rule for rule in RULES if rule.id == rule_id), None)