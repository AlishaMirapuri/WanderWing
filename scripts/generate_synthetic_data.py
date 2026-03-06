#!/usr/bin/env python3
"""
Synthetic data generator for the WanderWing experiment framework.

Simulates ~100 users across all 3 UX variants with realistic funnel drop-off curves.

Drop-off model:
  Variant A (Structured Preview):
    - 90% parse_accepted, 75% match_clicked, 60% recommendation_liked, 50% feedback_submitted
    - Interpretation: thorough UX builds confidence but adds friction

  Variant B (Fast to Matches):
    - 95% parse_accepted, 85% match_clicked, 55% recommendation_liked, 45% feedback_submitted
    - Interpretation: low friction drives CTR but lower downstream engagement

  Variant C (Explainable Matching):
    - 88% parse_accepted, 80% match_clicked, 78% recommendation_liked, 65% feedback_submitted
    - Interpretation: richer context → higher satisfaction and completion

Usage:
    python3 scripts/generate_synthetic_data.py
    python3 scripts/generate_synthetic_data.py --users 200 --clear
"""

import argparse
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
# Allow running from the project root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanderwing.core.event_logger import event_logger  # noqa: E402


# ── Drop-off configuration ────────────────────────────────────────────────────

VARIANT_DROPOFF = {
    "variant_a": {
        "profile_completed": 1.00,
        "parse_accepted": 0.90,
        "parse_edited": 0.08,   # ~8% go back and re-parse
        "match_clicked": 0.75,
        "recommendation_liked": 0.60,
        "feedback_submitted": 0.50,
    },
    "variant_b": {
        "profile_completed": 1.00,
        "parse_accepted": 0.95,
        "parse_edited": 0.04,   # fewer re-parses (less confirmation shown)
        "match_clicked": 0.85,
        "recommendation_liked": 0.55,
        "feedback_submitted": 0.45,
    },
    "variant_c": {
        "profile_completed": 1.00,
        "parse_accepted": 0.88,
        "parse_edited": 0.07,
        "match_clicked": 0.80,
        "recommendation_liked": 0.78,
        "feedback_submitted": 0.65,
    },
}

# Target user distribution across variants (matches traffic weights)
VARIANT_SHARES = {
    "variant_a": 0.40,
    "variant_b": 0.40,
    "variant_c": 0.20,
}

DESTINATIONS = ["Tokyo", "Paris", "Barcelona", "London", "New York"]
ACTIVITIES = ["HIKING", "FOOD_TOURS", "MUSEUMS", "BEACHES", "ADVENTURE_SPORTS", "SIGHTSEEING"]


def _random_timestamp(days_ago_max: int = 30) -> datetime:
    """Generate a random timestamp within the last N days."""
    delta = timedelta(
        days=random.uniform(0, days_ago_max),
        hours=random.uniform(0, 23),
        minutes=random.uniform(0, 59),
    )
    return datetime.now() - delta


def _simulate_user(user_id: str, variant: str, dropoff: dict) -> dict[str, int]:
    """
    Simulate one user's journey through the funnel.

    Returns a dict of event_type -> count logged.
    """
    base_ts = _random_timestamp(days_ago_max=30)
    logged: dict[str, int] = {}

    destination = random.choice(DESTINATIONS)
    activities = random.sample(ACTIVITIES, k=random.randint(2, 4))

    # profile_completed — always logs (100% rate)
    event_logger.log(
        user_id,
        variant,
        "profile_completed",
        {
            "name": f"User_{user_id[:6]}",
            "age_range": random.choice(["Under 25", "25-34", "35-44"]),
            "verification_level": random.randint(0, 4),
            "synthetic": True,
            "_ts": base_ts.isoformat(),
        },
    )
    logged["profile_completed"] = 1

    # parse_edited — some users re-parse before accepting
    if random.random() < dropoff["parse_edited"]:
        ts = base_ts + timedelta(minutes=random.uniform(2, 10))
        event_logger.log(
            user_id,
            variant,
            "parse_edited",
            {
                "destination": destination,
                "parse_attempt": 2,
                "synthetic": True,
                "_ts": ts.isoformat(),
            },
        )
        logged["parse_edited"] = 1

    # parse_accepted
    if random.random() < dropoff["parse_accepted"]:
        ts = base_ts + timedelta(minutes=random.uniform(5, 15))
        event_logger.log(
            user_id,
            variant,
            "parse_accepted",
            {
                "destination": destination,
                "duration": random.randint(5, 14),
                "synthetic": True,
                "_ts": ts.isoformat(),
            },
        )
        logged["parse_accepted"] = 1
    else:
        return logged  # dropped off before accepting parse

    # match_clicked
    if random.random() < dropoff["match_clicked"]:
        ts = base_ts + timedelta(minutes=random.uniform(10, 25))
        event_logger.log(
            user_id,
            variant,
            "match_clicked",
            {
                "rank": 1,
                "score": round(random.uniform(0.6, 0.95), 2),
                "name": random.choice(["Alice", "Bob", "Charlie", "Diana", "Erik"]),
                "synthetic": True,
                "_ts": ts.isoformat(),
            },
        )
        logged["match_clicked"] = 1
    else:
        return logged

    # recommendation_liked (0–N likes per user)
    liked_count = 0
    for _ in range(random.randint(1, 4)):
        if random.random() < dropoff["recommendation_liked"]:
            ts = base_ts + timedelta(minutes=random.uniform(20, 45))
            event_logger.log(
                user_id,
                variant,
                "recommendation_liked",
                {
                    "activity_id": f"activity_{random.randint(1, 5)}",
                    "name": random.choice(["Food Tour", "City Hike", "Museum Visit"]),
                    "rating": 1,
                    "synthetic": True,
                    "_ts": ts.isoformat(),
                },
            )
            liked_count += 1
    if liked_count:
        logged["recommendation_liked"] = liked_count

    # feedback_submitted
    if random.random() < dropoff["feedback_submitted"]:
        ts = base_ts + timedelta(minutes=random.uniform(40, 80))
        event_logger.log(
            user_id,
            variant,
            "feedback_submitted",
            {
                "rating": random.randint(3, 5),
                "accepted": random.random() > 0.35,
                "match_id": f"match_{random.randint(1, 5)}",
                "synthetic": True,
                "_ts": ts.isoformat(),
            },
        )
        logged["feedback_submitted"] = 1

    return logged


def generate(total_users: int = 100) -> None:
    """Seed the event store with `total_users` synthetic users."""
    print(f"\nGenerating {total_users} synthetic users across 3 variants…\n")

    variant_counts: dict[str, int] = {}
    event_totals: dict[str, int] = {}

    for v, share in VARIANT_SHARES.items():
        n = round(total_users * share)
        variant_counts[v] = n

    # Simulate users
    all_results: list[tuple[str, dict]] = []
    for variant, n_users in variant_counts.items():
        dropoff = VARIANT_DROPOFF[variant]
        for _ in range(n_users):
            # Use event_logger's assign_variant to ensure consistent hashing,
            # but override with target variant for synthetic seeding
            user_id = f"synthetic_{uuid.uuid4().hex[:12]}"
            result = _simulate_user(user_id, variant, dropoff)
            all_results.append((variant, result))
            for et, cnt in result.items():
                event_totals[et] = event_totals.get(et, 0) + cnt

    # ── Print summary ──────────────────────────────────────────────────────────
    print("=" * 60)
    print(f"{'Variant':<15} {'Users':>7}")
    print("-" * 60)
    for v, n in variant_counts.items():
        print(f"  {v:<13} {n:>7}")
    print("=" * 60)

    print("\nEvent totals across all variants:")
    print("=" * 60)
    for et in [
        "profile_completed",
        "parse_edited",
        "parse_accepted",
        "match_clicked",
        "recommendation_liked",
        "feedback_submitted",
    ]:
        print(f"  {et:<30} {event_totals.get(et, 0):>6}")
    print("=" * 60)

    # ── Live metrics ───────────────────────────────────────────────────────────
    print("\nComputed metrics from event store:")
    print("=" * 60)
    metrics = event_logger.compute_metrics()
    for variant, m in metrics.items():
        print(f"\n  {variant}:")
        print(f"    users             : {m.user_count}")
        print(f"    completion_rate   : {m.completion_rate:.2%}")
        print(f"    match_ctr         : {m.match_clickthrough_rate:.2%}")
        print(f"    rec_satisfaction  : {m.recommendation_satisfaction:.2f}")
        print(f"    parse_correction  : {m.parse_correction_rate:.2%}")
    print("=" * 60)
    print("\nDone! Launch Streamlit and navigate to 📊 Dashboard to see live charts.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed WanderWing experiment events")
    parser.add_argument(
        "--users",
        type=int,
        default=100,
        help="Total number of synthetic users to generate (default: 100)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing synthetic events before seeding",
    )
    args = parser.parse_args()

    if args.clear:
        from sqlalchemy import create_engine, text
        from wanderwing.utils.config import get_settings
        settings = get_settings()
        engine = create_engine(
            settings.database_url, connect_args={"check_same_thread": False}
        )
        with engine.connect() as conn:
            deleted = conn.execute(
                text("DELETE FROM experiment_events WHERE metadata_ LIKE '%synthetic%'")
            )
            conn.commit()
            print(f"Cleared {deleted.rowcount} synthetic rows.")

    generate(total_users=args.users)
