from typing import List


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
    if tier == 1:
        return [
            "Provide only verified public information from the approved knowledge base.",
            "If the answer is not present in the approved source set, escalate instead of guessing.",
        ]

    if tier == 2:
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
