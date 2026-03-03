"""
Demonstration script for matching engine functionality.

Shows the matching engine in action with example traveler pairs.
"""

import asyncio
import json
from datetime import date
from pathlib import Path

from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    DestinationStay,
    ParsedTravelerIntent,
    PacePreference,
)
from wanderwing.services.matching_engine import MatchingEngine


def create_tokyo_hiker() -> ParsedTravelerIntent:
    """Create a Tokyo hiker traveler."""
    return ParsedTravelerIntent(
        raw_input="Going to Tokyo April 1-10, love hiking and food tours, moderate budget",
        primary_destination="Tokyo",
        destination_stays=[
            DestinationStay(
                destination="Tokyo",
                country="Japan",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 10),
                nights=9,
                activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR],
                is_flexible=False,
                flexibility_days=0,
            )
        ],
        activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR, ActivityCategory.SIGHTSEEING],
        budget_tier=BudgetTier.MODERATE,
        budget_total_usd=1200.0,
        pace_preference=PacePreference.MODERATE,
        traveling_solo=True,
        open_to_companions=True,
        preferred_group_size=2,
        confidence_score=0.9,
        ambiguities=[],
        clarification_questions=[],
    )


def create_tokyo_adventurer() -> ParsedTravelerIntent:
    """Create a Tokyo adventurer (overlapping with hiker)."""
    return ParsedTravelerIntent(
        raw_input="Tokyo adventure trip April 5-12, hiking and outdoor sports",
        primary_destination="Tokyo",
        destination_stays=[
            DestinationStay(
                destination="Tokyo",
                country="Japan",
                start_date=date(2024, 4, 5),
                end_date=date(2024, 4, 12),
                nights=7,
                activities=[ActivityCategory.HIKING, ActivityCategory.ADVENTURE_SPORTS],
                is_flexible=False,
                flexibility_days=0,
            )
        ],
        activities=[
            ActivityCategory.HIKING,
            ActivityCategory.ADVENTURE_SPORTS,
            ActivityCategory.SIGHTSEEING,
        ],
        budget_tier=BudgetTier.MODERATE,
        pace_preference=PacePreference.MODERATE,
        traveling_solo=True,
        open_to_companions=True,
        preferred_group_size=2,
        confidence_score=0.85,
        ambiguities=[],
        clarification_questions=[],
    )


def create_tokyo_cultural() -> ParsedTravelerIntent:
    """Create a Tokyo cultural traveler (different activities)."""
    return ParsedTravelerIntent(
        raw_input="Tokyo cultural trip April 1-8, museums and temples, comfortable budget",
        primary_destination="Tokyo",
        destination_stays=[
            DestinationStay(
                destination="Tokyo",
                country="Japan",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 8),
                nights=7,
                activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS],
                is_flexible=False,
                flexibility_days=0,
            )
        ],
        activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS, ActivityCategory.SIGHTSEEING],
        budget_tier=BudgetTier.COMFORTABLE,
        pace_preference=PacePreference.RELAXED,
        traveling_solo=True,
        open_to_companions=True,
        preferred_group_size=2,
        confidence_score=0.9,
        ambiguities=[],
        clarification_questions=[],
    )


def create_paris_traveler() -> ParsedTravelerIntent:
    """Create a Paris traveler (different destination)."""
    return ParsedTravelerIntent(
        raw_input="Paris art and food tour April 1-7",
        primary_destination="Paris",
        destination_stays=[
            DestinationStay(
                destination="Paris",
                country="France",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 7),
                nights=6,
                activities=[ActivityCategory.MUSEUMS, ActivityCategory.FOOD_TOUR],
                is_flexible=False,
                flexibility_days=0,
            )
        ],
        activities=[ActivityCategory.MUSEUMS, ActivityCategory.FOOD_TOUR],
        budget_tier=BudgetTier.COMFORTABLE,
        pace_preference=PacePreference.RELAXED,
        traveling_solo=True,
        open_to_companions=True,
        confidence_score=0.9,
        ambiguities=[],
        clarification_questions=[],
    )


def print_separator(title: str):
    """Print a section separator."""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}\n")


def print_match_summary(match, traveler_a_name: str, traveler_b_name: str):
    """Print a formatted match summary."""
    if not match:
        print(f"❌ No match (filtered out by pre-filtering)\n")
        return

    exp = match.match_explanation

    print(f"✅ Match Found!")
    print(f"\n🎯 Overall Score: {exp.overall_score:.2f}")
    print(f"   - LLM Similarity: {exp.llm_similarity_score:.2f} (weight: 60%)")
    print(f"   - Rule-based Score: {exp.rule_based_score:.2f} (weight: 40%)")

    print(f"\n📍 Trip Details:")
    print(f"   - Destination: {match.destination}")
    print(f"   - Overlapping Days: {match.overlapping_days}")
    print(f"   - Trip Duration: {match.trip_duration_days} days")

    print(f"\n📊 Dimension Scores:")
    for ds in exp.dimension_scores[:5]:  # Top 5
        emoji = "🟢" if ds.score >= 0.8 else "🟡" if ds.score >= 0.6 else "🔴"
        print(f"   {emoji} {ds.dimension.value:20s} {ds.score:.2f} - {ds.explanation}")

    print(f"\n💡 Why Great Match:")
    for i, reason in enumerate(exp.why_great_match[:3], 1):
        print(f"   {i}. {reason}")

    print(f"\n💬 Conversation Starters:")
    for i, starter in enumerate(exp.conversation_starters[:3], 1):
        print(f"   {i}. \"{starter}\"")

    if exp.potential_concerns:
        print(f"\n⚠️  Potential Concerns:")
        for concern in exp.potential_concerns:
            print(f"   - {concern}")

    print()


async def test_match_pair(engine, traveler_a, traveler_b, a_name, b_name):
    """Test matching between two travelers."""
    print(f"Matching: {a_name} ↔ {b_name}")
    print(f"─" * 80)

    match = await engine.calculate_match(
        traveler_a=traveler_a,
        traveler_b=traveler_b,
        traveler_a_id=1,
        traveler_b_id=2,
        use_llm=False,  # Set to True to use actual LLM
    )

    print_match_summary(match, a_name, b_name)


async def main():
    """Run matching demonstrations."""
    print_separator("WanderWing Matching Engine Demonstration")

    print("This demo shows the matching engine with various traveler pairs.")
    print("Note: LLM calls are DISABLED by default (use_llm=False)")
    print("      Set use_llm=True and configure API keys to test with real LLM.\n")

    # Create travelers
    tokyo_hiker = create_tokyo_hiker()
    tokyo_adventurer = create_tokyo_adventurer()
    tokyo_cultural = create_tokyo_cultural()
    paris_traveler = create_paris_traveler()

    # Create engine
    engine = MatchingEngine()

    # Test Case 1: High compatibility (same destination, overlapping dates, shared activities)
    print_separator("Test Case 1: High Compatibility Match")
    print("📝 Scenario: Both hikers going to Tokyo with overlapping dates\n")
    await test_match_pair(
        engine, tokyo_hiker, tokyo_adventurer, "Tokyo Hiker (Apr 1-10)", "Tokyo Adventurer (Apr 5-12)"
    )

    # Test Case 2: Medium compatibility (same destination, different activities)
    print_separator("Test Case 2: Medium Compatibility Match")
    print("📝 Scenario: Same destination but different activity preferences\n")
    await test_match_pair(
        engine,
        tokyo_hiker,
        tokyo_cultural,
        "Tokyo Hiker (Apr 1-10)",
        "Tokyo Cultural Traveler (Apr 1-8)",
    )

    # Test Case 3: No match (different destinations)
    print_separator("Test Case 3: Incompatible Destinations")
    print("📝 Scenario: Different destinations (Tokyo vs Paris)\n")
    await test_match_pair(
        engine, tokyo_hiker, paris_traveler, "Tokyo Hiker (Apr 1-10)", "Paris Traveler (Apr 1-7)"
    )

    # Summary
    print_separator("Summary")
    print("✅ Demonstrated matching engine features:")
    print("   1. ✅ Pre-filtering (destination, date overlap)")
    print("   2. ✅ Dimension-by-dimension scoring (7 dimensions)")
    print("   3. ✅ Rule-based scoring (Jaccard, budget tiers, etc.)")
    print("   4. ✅ Hybrid score calculation (60% LLM + 40% rules)")
    print("   5. ✅ Match explanation generation")
    print("   6. ✅ Graceful handling of incompatible pairs")
    print()
    print("💡 To test with real LLM:")
    print("   1. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
    print("   2. Change use_llm=False to use_llm=True in test_match_pair()")
    print("   3. Run: python scripts/test_matching_demo.py")
    print()
    print("📖 For detailed design decisions, see: MATCHING_ENGINE_DESIGN.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
