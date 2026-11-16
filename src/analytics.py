from dataclasses import dataclass, asdict


@dataclass
class Event:
    category: str
    tier: int
    escalated: bool


def summarize(events):
    if not events:
        return {
            "total_cases": 0,
            "escalated_cases": 0,
            "escalation_rate": 0.0,
            "tier4_cases": 0,
        }

    total = len(events)
    escalated = sum(1 for e in events if e.escalated)
    tier4 = sum(1 for e in events if e.tier == 4)

    return {
        "total_cases": total,
        "escalated_cases": escalated,
        "escalation_rate": escalated / total,
        "tier4_cases": tier4,
    }
