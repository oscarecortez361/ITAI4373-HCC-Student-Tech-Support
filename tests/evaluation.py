from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation_engine import evaluate_cases


def main():
    metrics, _ = evaluate_cases()
    print(f"Cases: {metrics['total_cases']}")
    print(f"Category accuracy: {metrics['category_accuracy']:.1%}")
    print(f"Tier accuracy: {metrics['tier_accuracy']:.1%}")
    print(f"Tier 4 recall: {metrics['tier4_recall']:.1%}")
    print(f"False safe answers: {metrics['false_safe_answers']}")
    print(f"Escalation rate: {metrics['escalation_rate']:.1%}")


if __name__ == "__main__":
    main()
