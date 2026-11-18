"""Approved guidance for each delegation tier.

What the system is allowed to say depends on the tier. Tier 1 sticks to
verified public information. Tier 2 uses a fixed playbook. Tier 3 only
collects a short description for a human. Tier 4 stops and escalates. Nothing
here is generated, it is all fixed text so we can review it ahead of time.
"""
from typing import List


# Playbooks exist only for the three Tier 2 categories: Canvas, Browser/Device
# and Wi-Fi. Each one ends with an escalation step so the student is never left
# at a dead end.
PLAYBOOKS = {
    "Canvas / Eagle Online": [
        "Confirm that the student is using the current official HCC access route.",
        "Try a supported browser or private/incognito window.",
        "Clear browser cache and cookies if the page is looping or loading incorrectly.",
        "If the problem is account-specific or persists after basic troubleshooting, escalate to human support.",
    ],
    "Browser / Device": [
        "Restart the browser.",
        "Try a private/incognito window.",
        "Clear cache and cookies.",
        "Try another supported browser if available.",
        "If the issue continues, route to human support with the browser/device details.",
    ],
    "Wi-Fi / Connectivity": [
        "Confirm Wi-Fi is enabled on the device.",
        "Disconnect and reconnect to the network.",
        "Restart the device if the connection remains unstable.",
        "If authentication or account credentials are involved, stop and escalate.",
    ],
}


def get_guidance(category: str, tier: int) -> List[str]:
    """Return the list of next-step lines to show for a routed case.

    category: predicted category, used only to pick a Tier 2 playbook.
    tier: delegation tier from 1 to 4.
    Returns plain-text steps. Any tier other than 1, 2 or 3 gets the Tier 4
    stop-and-escalate text, which is the safe default.
    """
    if tier == 1:
        return [
            "Provide only verified public information from the approved knowledge base.",
            "If the answer is not present in the approved source set, escalate instead of guessing.",
        ]

    if tier == 2:
        # A Tier 2 category without a playbook still gets a generic low-risk line.
        return PLAYBOOKS.get(
            category,
            ["Use low-risk troubleshooting only. Escalate if the issue remains unresolved."]
        )

    if tier == 3:
        return [
            "Collect a short problem description without requesting passwords or sensitive personal data.",
            "Create a structured summary for human review.",
            "Do not perform account changes or identity verification.",
        ]

    return [
        "Stop autonomous troubleshooting.",
        "Do not request or display passwords, MFA codes, security answers, or sensitive personal data.",
        "Escalate to authorized human support.",
    ]
