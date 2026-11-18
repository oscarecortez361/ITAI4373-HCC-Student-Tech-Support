"""Session analytics for the live demo.

We keep three fields per case (category, tier, escalated) and nothing else.
The raw message text is never stored here. The events live in the Streamlit
session only, so they are gone when the session ends or the Clear button is
pressed.
"""
from dataclasses import dataclass, asdict


@dataclass
class Event:
    """One routed case: its category, its tier, and whether a human is required."""
    category: str
    tier: int
    escalated: bool


def summarize(events):
    """Count cases for the session analytics panel.

    events: list of Event objects from this session (may be empty).
    Returns a dict with total_cases, escalated_cases, escalation_rate (0.0 to
    1.0) and tier4_cases. An empty list returns zeros, not a divide by zero.
    """
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
