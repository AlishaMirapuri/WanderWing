"""Unit tests for matching logic."""

from datetime import date

import pytest

from wanderwing.core.matching import (
    _calculate_activity_similarity,
    _calculate_budget_compatibility,
    _calculate_date_overlap,
    _calculate_destination_overlap,
)
from wanderwing.schemas.trip import ParsedItinerary


def test_destination_overlap_exact_match():
    """Test destination overlap with exact match."""
    trip1 = ParsedItinerary(destination="Tokyo")
    trip2 = ParsedItinerary(destination="Tokyo")

    score = _calculate_destination_overlap(trip1, trip2)
    assert score == 1.0


def test_destination_overlap_no_match():
    """Test destination overlap with no match."""
    trip1 = ParsedItinerary(destination="Tokyo")
    trip2 = ParsedItinerary(destination="Paris")

    score = _calculate_destination_overlap(trip1, trip2)
    assert score == 0.0


def test_date_overlap_full():
    """Test full date overlap."""
    trip1 = ParsedItinerary(
        destination="Tokyo",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 10),
    )
    trip2 = ParsedItinerary(
        destination="Tokyo",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 10),
    )

    score = _calculate_date_overlap(trip1, trip2)
    assert score == 1.0


def test_date_overlap_partial():
    """Test partial date overlap."""
    trip1 = ParsedItinerary(
        destination="Tokyo",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 10),
    )
    trip2 = ParsedItinerary(
        destination="Tokyo",
        start_date=date(2024, 4, 5),
        end_date=date(2024, 4, 15),
    )

    score = _calculate_date_overlap(trip1, trip2)
    assert 0.0 < score < 1.0


def test_date_overlap_none():
    """Test no date overlap."""
    trip1 = ParsedItinerary(
        destination="Tokyo",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 10),
    )
    trip2 = ParsedItinerary(
        destination="Tokyo",
        start_date=date(2024, 4, 11),
        end_date=date(2024, 4, 20),
    )

    score = _calculate_date_overlap(trip1, trip2)
    assert score == 0.0


def test_activity_similarity():
    """Test activity similarity calculation."""
    from wanderwing.schemas.trip import ActivityType

    trip1 = ParsedItinerary(
        destination="Tokyo",
        activities=[ActivityType.HIKING, ActivityType.FOOD_TOUR, ActivityType.SIGHTSEEING],
    )
    trip2 = ParsedItinerary(
        destination="Tokyo",
        activities=[ActivityType.FOOD_TOUR, ActivityType.SIGHTSEEING, ActivityType.SHOPPING],
    )

    score = _calculate_activity_similarity(trip1, trip2)
    # 2 common activities (food_tour, sightseeing) out of 4 total unique
    assert score == 0.5


def test_budget_compatibility_same_tier():
    """Test budget compatibility with same tier."""
    trip1 = ParsedItinerary(destination="Tokyo", budget_tier="moderate")
    trip2 = ParsedItinerary(destination="Tokyo", budget_tier="moderate")

    score = _calculate_budget_compatibility(trip1, trip2)
    assert score == 1.0


def test_budget_compatibility_adjacent_tiers():
    """Test budget compatibility with adjacent tiers."""
    trip1 = ParsedItinerary(destination="Tokyo", budget_tier="moderate")
    trip2 = ParsedItinerary(destination="Tokyo", budget_tier="comfortable")

    score = _calculate_budget_compatibility(trip1, trip2)
    assert score == 0.75  # 1 tier apart = 0.25 penalty
