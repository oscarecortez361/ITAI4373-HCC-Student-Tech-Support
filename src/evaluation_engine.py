"""Evaluation engine: runs the labeled synthetic cases through the routing logic.

Each row of data/synthetic_test_cases.csv has an issue, an expected category
and an expected tier. We send the issue through the same three functions the
Streamlit app uses (inspect_input, classify_issue, assign_tier) and compare
the result to the labels. Nothing here is a separate copy of the logic, so a
change to the rules shows up in these numbers right away.

Caveat: the same 100 cases were used to find failures and tune the rules from
v4 to v6. That makes this a regression set, not a held-out benchmark. A score
of 100% tells us the rules still match our labels. It does not tell us how
they do on real student messages.
"""
from pathlib import Path
import csv
import json

from src.input_guard import inspect_input
from src.classifier import classify_issue
from src.delegation import assign_tier

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "synthetic_test_cases.csv"


def evaluate_cases():
    """Run every labeled case through the routing logic and score it.

    Returns a tuple of (metrics, results).

    metrics is a dict with:
        total_cases: number of rows in the CSV.
        category_accuracy: share of cases where the predicted category
            equals the expected category.
        tier_accuracy: share of cases where the predicted tier equals the
            expected tier.
        tier4_total / tier4_caught: cases labeled Tier 4, and how many of
            those we also routed to Tier 4.
        tier4_recall: tier4_caught / tier4_total.
        false_safe_answers: cases labeled Tier 4 that we routed below Tier 4.
            This is the number we care about most, and it should stay at 0.
        escalation_rate: share of all cases with human_required set
            (Tier 3 or Tier 4).

    results is a list of dicts, one per case, with the expected and predicted
    values side by side. The dashboard shows it and offers it as a CSV.
    """
    rows = list(csv.DictReader(DATA_FILE.open(encoding="utf-8")))

    results = []
    category_correct = 0
    tier_correct = 0
    tier4_total = 0
    tier4_caught = 0
    false_safe_answers = 0

    for row in rows:
        issue = row["issue"]
        expected_category = row["expected_category"]
        expected_tier = int(row["expected_tier"])

        # Same three calls, same order, as the live app.
        guard = inspect_input(issue)
        classification = classify_issue(issue)
        decision = assign_tier(
            classification.category,
            guard.force_tier4,
            guard.reasons,
        )

        category_ok = classification.category == expected_category
        tier_ok = decision.tier == expected_tier

        category_correct += int(category_ok)
        tier_correct += int(tier_ok)

        # Tier 4 bookkeeping. A false safe answer is a case that should have
        # been a hard stop and was routed to a lower tier.
        if expected_tier == 4:
            tier4_total += 1
            if decision.tier == 4:
                tier4_caught += 1
            if decision.tier < 4:
                false_safe_answers += 1

        results.append({
            "issue": issue,
            "expected_category": expected_category,
            "predicted_category": classification.category,
            "category_correct": category_ok,
            "expected_tier": expected_tier,
            "predicted_tier": decision.tier,
            "tier_correct": tier_ok,
            "classifier_confidence": classification.confidence,
            "human_required": decision.human_required,
        })

    total = len(rows)

    # The "if total" and "if tier4_total" checks only avoid dividing by zero
    # when a CSV is empty.
    metrics = {
        "total_cases": total,
        "category_accuracy": category_correct / total if total else 0.0,
        "tier_accuracy": tier_correct / total if total else 0.0,
        "tier4_recall": tier4_caught / tier4_total if tier4_total else 0.0,
        "tier4_total": tier4_total,
        "tier4_caught": tier4_caught,
        "false_safe_answers": false_safe_answers,
        "escalation_rate": sum(1 for r in results if r["human_required"]) / total if total else 0.0,
    }

    return metrics, results


if __name__ == "__main__":
    metrics, results = evaluate_cases()
    print(f"Cases: {metrics['total_cases']}")
    print(f"Category accuracy: {metrics['category_accuracy']:.1%}")
    print(f"Tier accuracy: {metrics['tier_accuracy']:.1%}")
    print(f"Tier 4 recall: {metrics['tier4_recall']:.1%}")
    print(f"Tier 4 false safe answers: {metrics['false_safe_answers']}")
    print(f"Escalation rate: {metrics['escalation_rate']:.1%}")
