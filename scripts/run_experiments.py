"""Run and analyze A/B experiments."""

from collections import defaultdict

from wanderwing.db import Experiment, SessionLocal


def analyze_experiment(experiment_name: str) -> None:
    """
    Analyze results for an experiment.

    Args:
        experiment_name: Name of the experiment to analyze
    """
    db = SessionLocal()
    try:
        # Fetch experiment data
        experiments = db.query(Experiment).filter(
            Experiment.name == experiment_name
        ).all()

        if not experiments:
            print(f"No data found for experiment: {experiment_name}")
            return

        # Group by variant
        variant_stats = defaultdict(lambda: {"total": 0, "converted": 0})

        for exp in experiments:
            variant = exp.variant
            variant_stats[variant]["total"] += 1
            if exp.converted:
                variant_stats[variant]["converted"] += 1

        # Print results
        print(f"\n=== Experiment: {experiment_name} ===\n")

        for variant, stats in variant_stats.items():
            total = stats["total"]
            converted = stats["converted"]
            conversion_rate = (converted / total * 100) if total > 0 else 0

            print(f"Variant: {variant}")
            print(f"  Total: {total}")
            print(f"  Converted: {converted}")
            print(f"  Conversion Rate: {conversion_rate:.2f}%")
            print()

    finally:
        db.close()


def list_experiments() -> None:
    """List all experiments with data."""
    db = SessionLocal()
    try:
        experiments = db.query(Experiment.name).distinct().all()
        experiment_names = [exp[0] for exp in experiments]

        if not experiment_names:
            print("No experiments found")
            return

        print("\nAvailable experiments:")
        for name in experiment_names:
            print(f"  - {name}")
        print()

    finally:
        db.close()


def main() -> None:
    """Main function."""
    print("A/B Experiment Analysis Tool")
    print("=" * 50)

    list_experiments()

    # Analyze specific experiments
    experiments_to_analyze = [
        "itinerary_extraction_prompt",
        "matching_algorithm",
    ]

    for exp_name in experiments_to_analyze:
        analyze_experiment(exp_name)


if __name__ == "__main__":
    main()
