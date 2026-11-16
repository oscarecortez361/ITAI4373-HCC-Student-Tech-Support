from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DelegationDecision:
    tier: int
    tier_name: str
    total_score: int
    scores: Dict[str, int]
    reasons: List[str]
    human_required: bool


TIER_NAMES = {
    1: "Public information / approved FAQ",
    2: "Guided low-risk troubleshooting",
    3: "AI-assisted human support / routing",
    4: "Human-controlled security or account action",
}


def assign_tier(category: str, guard_force_tier4: bool, guard_reasons: List[str]) -> DelegationDecision:
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

    # Conservative tier mapping for the POC.
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
