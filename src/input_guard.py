"""Input guard: the safety check that runs before anything else.

This is the first stop for every student message. It looks for account
compromise, MFA or identity issues, shared credentials, requests for the
system to do an account action, and anything that looks like an SSN, student
ID or card number. If any of those hit, force_tier4 is set and the later steps
cannot lower it. The classifier can get the category wrong and the case still
ends up with a human.

Everything here is plain regular expressions. No model is involved, so the
same input always gives the same answer and we can test it.
"""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class GuardResult:
    """What the guard found.

    force_tier4: True if any trigger fired.
    reasons: plain-language names of each trigger, shown in the UI and passed
        into the handoff summary.
    contains_sensitive_data: True only for the SSN, ID or card patterns.
    """
    force_tier4: bool
    reasons: List[str]
    contains_sensitive_data: bool


# Each key is the reason text the student-facing UI will show. The patterns are
# checked against lowercased text with word boundaries. "reset my password for
# me" is here but "I forgot my password" is not on purpose: asking for help with
# a password is a Tier 3 routing question, asking the system to do the reset is
# a Tier 4 account action.
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

# Patterns for values that should never be typed into this tool. These are
# deliberately broad. The card pattern will also catch some long digit strings
# that are not cards, and that is fine, because a false Tier 4 costs a person a
# quick look and a miss costs a lot more.
SENSITIVE_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",          # SSN-like
    r"\b\d{9}\b",                      # possible student/ID number
    r"\b(?:\d[ -]*?){13,16}\b",        # card-like
]


def inspect_input(text: str) -> GuardResult:
    """Scan one student message and report whether it must go to Tier 4.

    text: the raw message the student typed.
    Returns a GuardResult. Each trigger group is listed at most once, even if
    several of its patterns match.
    """
    lowered = text.lower()
    reasons = []

    # One hit per group is enough, so break after the first matching pattern.
    for reason, patterns in SECURITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                reasons.append(reason)
                break

    # Digit patterns run on the original text, not the lowercased copy.
    contains_sensitive = any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in SENSITIVE_PATTERNS
    )

    if contains_sensitive:
        reasons.append("possible sensitive personal data")

    # Any reason at all means Tier 4. There is no score or threshold here.
    return GuardResult(
        force_tier4=bool(reasons),
        reasons=reasons,
        contains_sensitive_data=contains_sensitive,
    )
