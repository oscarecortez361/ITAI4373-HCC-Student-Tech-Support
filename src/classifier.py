"""Issue classifier: puts a student message into one support category.

The classifier is a set of keyword lists checked in a fixed order. The first
list with at least one hit wins, so there is no tie-break step. The order is:

    1. Account Security / Compromise
    2. Microsoft 365 / Student Email
    3. Canvas / Eagle Online
    4. Wi-Fi / Connectivity
    5. Browser / Device
    6. General Routing
    7. Password / Login
    8. Unknown / Human Review (nothing matched, confidence 0.35)

Named services sit above generic sign-in wording on purpose. "Canvas login
failed" is a Canvas issue, not a plain password issue.

Matching is plain substring matching on the lowercased text, with no word
boundaries. Short keywords can hit inside longer words ("edge" inside
"knowledge", "teams" inside "steams"). This is a known limitation of the POC.
The input guard runs separately and can still force Tier 4 whatever category
comes out of here.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class ClassificationResult:
    """Result of classify_issue.

    category: one of the eight category names listed in the module docstring.
    confidence: a display value between 0.35 and 0.99. It is built from the
        number of keyword matches, not a calibrated probability.
    matched_keywords: the keywords that hit, empty for Unknown.
    """
    category: str
    confidence: float
    matched_keywords: List[str]


# Keyword lists, one per category. All entries are lowercase because the input
# is lowercased before matching.
SECURITY_KEYWORDS = [
    "hacked", "compromised", "unauthorized", "mfa", "2fa",
    "two-factor", "two factor", "authenticator", "someone changed",
    "someone got into", "without permission", "security settings",
    "account were stolen", "account was stolen", "password and account were stolen",
]

EMAIL_KEYWORDS = [
    "outlook", "student email", "school email", "hcc email", "mailbox",
    "office 365", "microsoft 365", "teams", "onedrive"
]

CANVAS_KEYWORDS = [
    "canvas", "eagle online", "course page", "assignment page",
    "module", "discussion page", "course content"
]

# v6 added generic internet wording here. The 100-case run missed "The internet
# works for a minute and then disconnects" as a connectivity issue, and this fix
# was the last change before every labeled case matched.
WIFI_KEYWORDS = [
    "wifi", "wi-fi", "wireless", "internet", "internet connection", "network"
]

BROWSER_KEYWORDS = [
    "browser", "chrome", "edge", "firefox", "cache", "cookies",
    "incognito", "private window", "laptop browser"
]

ROUTING_KEYWORDS = [
    "tech support", "technical support", "technology support",
    "technology help", "technical help", "technical assistance",
    "help desk", "support page", "support office", "support contact",
    "right contact", "where do i go", "where should i go",
    "where can i find", "who do i contact", "who handles",
    "where can students find"
]

LOGIN_KEYWORDS = [
    "login", "log in", "sign in", "password", "username",
    "locked out", "login failed"
]


def _matches(text: str, keywords: List[str]) -> List[str]:
    """Return the keywords that appear anywhere in text (substring match)."""
    return [kw for kw in keywords if kw in text]


def classify_issue(text: str) -> ClassificationResult:
    """Pick one category for a student message.

    text: the raw message. It is lowercased here.
    Returns a ClassificationResult. Confidence is a base value plus a fixed
    step per matched keyword, capped per category:
        Security: 0.82 + 0.04 per match, cap 0.99
        Email: 0.72 + 0.05 per match, cap 0.97
        Canvas: 0.65 + 0.05 per match, cap 0.97
        Wi-Fi, Browser, Routing, Login: 0.65 + 0.05 per match, cap 0.95
        Unknown: fixed 0.35
    """
    lowered = text.lower()

    # 1. Security gets highest semantic priority.
    matches = _matches(lowered, SECURITY_KEYWORDS)
    if matches:
        return ClassificationResult(
            "Account Security / Compromise",
            min(0.99, 0.82 + 0.04 * len(matches)),
            matches,
        )

    # 2. Named platforms/services beat generic sign-in wording.
    matches = _matches(lowered, EMAIL_KEYWORDS)
    if matches:
        return ClassificationResult(
            "Microsoft 365 / Student Email",
            min(0.97, 0.72 + 0.05 * len(matches)),
            matches,
        )

    matches = _matches(lowered, CANVAS_KEYWORDS)
    if matches:
        return ClassificationResult(
            "Canvas / Eagle Online",
            min(0.97, 0.65 + 0.05 * len(matches)),
            matches,
        )

    matches = _matches(lowered, WIFI_KEYWORDS)
    if matches:
        return ClassificationResult(
            "Wi-Fi / Connectivity",
            min(0.95, 0.65 + 0.05 * len(matches)),
            matches,
        )

    matches = _matches(lowered, BROWSER_KEYWORDS)
    if matches:
        return ClassificationResult(
            "Browser / Device",
            min(0.95, 0.65 + 0.05 * len(matches)),
            matches,
        )

    matches = _matches(lowered, ROUTING_KEYWORDS)
    if matches:
        return ClassificationResult(
            "General Routing",
            min(0.95, 0.65 + 0.05 * len(matches)),
            matches,
        )

    matches = _matches(lowered, LOGIN_KEYWORDS)
    if matches:
        return ClassificationResult(
            "Password / Login",
            min(0.95, 0.65 + 0.05 * len(matches)),
            matches,
        )

    # Nothing matched. We do not guess, this goes to a human at Tier 3.
    return ClassificationResult(
        category="Unknown / Human Review",
        confidence=0.35,
        matched_keywords=[],
    )
