import re
from dataclasses import dataclass
from typing import List


@dataclass
class GuardResult:
    force_tier4: bool
    reasons: List[str]
    contains_sensitive_data: bool


SECURITY_PATTERNS = {
    "suspected account compromise": [
        r"\bhacked\b",
        r"\bcompromised\b",
        r"\bsomeone (changed|got into|accessed)\b",
        r"\bunauthorized\b",
        r"\bstolen account\b",
        r"\baccount (was|were) stolen\b",
        r"\bpassword.*stolen\b",
    ],
    "MFA or identity security issue": [
        r"\bmfa\b",
        r"\b2fa\b",
        r"\btwo[- ]factor\b",
        r"\bauthenticator\b",
        r"\bidentity verification\b",
        r"\bverify my identity\b",
    ],
    "credential disclosure": [
        r"\bmy password is\b",
        r"\bpassword:\s*\S+",
        r"\bpin is\b",
        r"\bsecurity answer\b",
    ],
    "account administration request": [
        r"\breset my password for me\b",
        r"\bchange my password for me\b",
        r"\bunlock my account\b",
        r"\bdisable mfa\b",
        r"\bremove mfa\b",
        r"\bchange my email\b",
    ],
}

SENSITIVE_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",          # SSN-like
    r"\b\d{9}\b",                      # possible student/ID number
    r"\b(?:\d[ -]*?){13,16}\b",        # card-like
]


def inspect_input(text: str) -> GuardResult:
    lowered = text.lower()
    reasons = []

    for reason, patterns in SECURITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                reasons.append(reason)
                break

    contains_sensitive = any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in SENSITIVE_PATTERNS
    )

    if contains_sensitive:
        reasons.append("possible sensitive personal data")

    return GuardResult(
        force_tier4=bool(reasons),
        reasons=reasons,
        contains_sensitive_data=contains_sensitive,
    )
