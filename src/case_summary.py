import re


def _redact_sensitive_text(text: str) -> str:
    """Redact common sensitive values before including user text in a handoff summary."""
    redacted = text

    substitutions = [
        (r"(?i)\bmy password is\s+\S+", "my password is [REDACTED]"),
        (r"(?i)\bpassword:\s*\S+", "password: [REDACTED]"),
        (r"(?i)\bpin is\s+\S+", "PIN is [REDACTED]"),
        (r"(?i)\bsecurity answer(?:\s+is|:)?\s+\S+", "security answer [REDACTED]"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED SSN-LIKE DATA]"),
        (r"\b\d{9}\b", "[REDACTED ID-LIKE DATA]"),
        (r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED CARD-LIKE DATA]"),
    ]

    for pattern, replacement in substitutions:
        redacted = re.sub(pattern, replacement, redacted)

    return redacted


def build_case_summary(issue_text: str, category: str, tier: int, reasons: list[str]) -> str:
    safe_text = _redact_sensitive_text(issue_text.strip())
    if len(safe_text) > 500:
        safe_text = safe_text[:500] + "..."

    reason_text = "; ".join(reasons) if reasons else "No special safety trigger detected."

    requested_action = (
        "Authorized human review required. Do not perform account changes in the POC."
        if tier == 4
        else "Human review and appropriate routing if unresolved."
    )

    return (
        f"Issue summary: {safe_text}\n"
        f"Category: {category}\n"
        f"Delegation tier: Tier {tier}\n"
        f"Routing reason: {reason_text}\n"
        f"Requested action: {requested_action}"
    )
