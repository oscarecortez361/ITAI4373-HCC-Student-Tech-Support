from dataclasses import dataclass
from typing import List


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    matched_keywords: List[str]


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
    return [kw for kw in keywords if kw in text]


def classify_issue(text: str) -> ClassificationResult:
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

    return ClassificationResult(
        category="Unknown / Human Review",
        confidence=0.35,
        matched_keywords=[],
    )
