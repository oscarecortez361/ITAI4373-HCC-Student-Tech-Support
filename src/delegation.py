"""Delegation engine: decides how much the system is allowed to do.

The four tiers give the system less authority as the cost of a wrong answer
goes up:

    Tier 1: public information only
    Tier 2: guided low-risk troubleshooting
    Tier 3: human review and routing
    Tier 4: human-controlled security or account action (hard stop)

Two rules drive the result. First, if the input guard fired, the answer is
Tier 4 and nothing else is looked at. Second, otherwise the tier comes from the
category alone. Each category also carries five risk scores (financial,
operational, reputational, task complexity, human expertise), each from 1 to 5,
so the total is at most 25. Those scores are shown in the UI to explain the
decision. They do not calculate the tier.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DelegationDecision:
    """Result of assign_tier.

    tier: 1 to 4.
    tier_name: the label from TIER_NAMES.
    total_score: sum of the five risk scores (display only).
    scores: the five risk scores by name.
    reasons: why this tier was chosen, shown in the UI and handoff summary.
    human_required: True for Tier 3 and Tier 4.
    """
    tier: int
    tier_name: str
    total_score: int
    scores: Dict[str, int]
    reasons: List[str]
    human_required: bool


TIER_NAMES = {
    1: "Public information / approved FAQ",
    2: "Guided low-risk troubleshooting",
    3: "Human review / routing",
    4: "Human-controlled security or account action",
}


def assign_tier(category: str, guard_force_tier4: bool, guard_reasons: List[str]) -> DelegationDecision:
    """Assign a delegation tier.

    category: the classifier's category name.
    guard_force_tier4: True if the input guard fired.
    guard_reasons: the guard's reason text, copied into the decision.
    Returns a DelegationDecision. An unrecognized category falls back to the
    Unknown / Human Review scores and Tier 3.
    """
    # Guard override comes first. It uses the same scores as the Security
    # category, whatever the classifier said.
    if guard_force_tier4:
        scores = {
            "financial_risk": 4,
            "operational_risk": 5,
            "reputational_risk": 5,
            "task_complexity": 4,
            "human_expertise": 5,
        }
        return DelegationDecision(
            tier=4,
            tier_name=TIER_NAMES[4],
            total_score=sum(scores.values()),
            scores=scores,
            reasons=["Tier 4 hard override"] + guard_reasons,
            human_required=True,
        )

    # Risk scores per category, 1 (low) to 5 (high). Display only.
    category_scores = {
        "Account Security / Compromise": {
            "financial_risk": 4,
            "operational_risk": 5,
            "reputational_risk": 5,
            "task_complexity": 4,
            "human_expertise": 5,
        },
        "General Routing": {
            "financial_risk": 1,
            "operational_risk": 1,
            "reputational_risk": 2,
            "task_complexity": 1,
            "human_expertise": 1,
        },
        "Canvas / Eagle Online": {
            "financial_risk": 1,
            "operational_risk": 2,
            "reputational_risk": 2,
            "task_complexity": 2,
            "human_expertise": 2,
        },
        "Browser / Device": {
            "financial_risk": 1,
            "operational_risk": 2,
            "reputational_risk": 2,
            "task_complexity": 2,
            "human_expertise": 2,
        },
        "Wi-Fi / Connectivity": {
            "financial_risk": 1,
            "operational_risk": 2,
            "reputational_risk": 2,
            "task_complexity": 2,
            "human_expertise": 2,
        },
        "Microsoft 365 / Student Email": {
            "financial_risk": 2,
            "operational_risk": 3,
            "reputational_risk": 3,
            "task_complexity": 3,
            "human_expertise": 3,
        },
        "Password / Login": {
            "financial_risk": 2,
            "operational_risk": 3,
            "reputational_risk": 3,
            "task_complexity": 3,
            "human_expertise": 3,
        },
        "Unknown / Human Review": {
            "financial_risk": 2,
            "operational_risk": 3,
            "reputational_risk": 3,
            "task_complexity": 4,
            "human_expertise": 4,
        },
    }

    scores = category_scores.get(category, category_scores["Unknown / Human Review"])
    total = sum(scores.values())

    # Conservative tier mapping for the POC. Tier comes from the category, not
    # from total. Anything not listed (Microsoft 365, Password / Login, Unknown)
    # lands on Tier 3 so a person reviews it.
    if category == "Account Security / Compromise":
        tier = 4
    elif category == "General Routing":
        tier = 1
    elif category in {"Canvas / Eagle Online", "Browser / Device", "Wi-Fi / Connectivity"}:
        tier = 2
    else:
        tier = 3

    return DelegationDecision(
        tier=tier,
        tier_name=TIER_NAMES[tier],
        total_score=total,
        scores=scores,
        reasons=[f"Assigned from category: {category}"],
        human_required=tier >= 3,
    )
