from pathlib import Path
import csv
import json

from src.input_guard import inspect_input
from src.classifier import classify_issue
from src.delegation import assign_tier

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "synthetic_test_cases.csv"


def evaluate_cases():
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
    print(f"False safe answers: {metrics['false_safe_answers']}")
    print(f"Escalation rate: {metrics['escalation_rate']:.1%}")
