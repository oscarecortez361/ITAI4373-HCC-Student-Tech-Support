"""Command line runner for the 100-case synthetic evaluation.

Usage, from anywhere:
    python tests/evaluation.py

It prints the same five numbers the Evaluation Dashboard shows. Expected for
the v6 baseline: 100 cases, 100.0% category accuracy, 100.0% tier accuracy,
100.0% Tier 4 recall, 0 false safe answers, 45.0% escalation rate.
"""
from pathlib import Path
import sys

# Put the repo root on the import path so "from src..." works no matter which
# directory the script is launched from.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation_engine import evaluate_cases


def main():
    """Run the evaluation and print the summary metrics."""
    metrics, _ = evaluate_cases()
    print(f"Cases: {metrics['total_cases']}")
    print(f"Category accuracy: {metrics['category_accuracy']:.1%}")
    print(f"Tier accuracy: {metrics['tier_accuracy']:.1%}")
    print(f"Tier 4 recall: {metrics['tier4_recall']:.1%}")
    print(f"False safe answers: {metrics['false_safe_answers']}")
    print(f"Escalation rate: {metrics['escalation_rate']:.1%}")


if __name__ == "__main__":
    main()
