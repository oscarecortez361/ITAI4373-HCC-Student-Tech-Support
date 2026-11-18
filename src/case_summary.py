"""Human handoff summary for Tier 3 and Tier 4 cases.

When a case needs a person, we build a short text block with the issue,
category, tier, routing reason and requested action, so the student does not
have to start the explanation over. The student's own words go in the summary,
so they are redacted first: passwords, PINs, security answers, SSN-like values,
9-digit ID-like values and card-like numbers.
"""
import re


def _redact_sensitive_text(text: str) -> str:
    """Redact common sensitive values before including user text in a handoff summary."""
    redacted = text

    # Order matters a little: the specific SSN pattern runs before the generic
    # 9-digit and card patterns so it gets the more precise label. This is
    # pattern matching, so it will not catch every format a student could type.
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
    """Build the redacted handoff text a human reviewer will read.

    issue_text: the raw student message (redacted here before it is used).
    category: predicted category from the classifier.
    tier: delegation tier, 3 or 4 in normal use.
    reasons: routing reasons from the delegation engine.
    Returns a five-line plain-text summary.
    """
    # Redact first, then cap the length, so the 500 character limit applies to
    # the text a reviewer actually sees.
    safe_text = _redact_sensitive_text(issue_text.strip())
    if len(safe_text) > 500:
        safe_text = safe_text[:500] + "..."

    reason_text = "; ".join(reasons) if reasons else "No special safety trigger detected."

    # Tier 4 asks for an authorized person and says plainly that the POC does
    # not touch accounts. Tier 3 only asks for review and routing.
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
