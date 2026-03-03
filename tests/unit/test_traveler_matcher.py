"""
Comprehensive unit tests for TravelerMatcher.

Tests cover:
- Deterministic filters (destination, dates, age, safety)
- Semantic scoring (activities, budget, pace, social, age)
- Match score calculation
- Confidence calculation
- Edge cases and missing data
"""

from datetime import date, datetime, timedelta

import pytest

from wanderwing.schemas.profile import AgeRange, Gender, TravelerProfile
from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    DestinationStay,
    PacePreference,
    ParsedTravelerIntent,
)
from wanderwing.services.traveler_matcher import (
    DeterministicFilters,
    MatchReason,
    SafetyFlag,
    SemanticScorer,
    TravelerMatcher,
)


# Test Fixtures

@pytest.fixture
def tokyo_hiker_profile():
    """Profile for a Tokyo hiker."""
    return TravelerProfile(
        id=1,
        user_id=1,
        name="Alice",
        email="alice@example.com",
        age_range=AgeRange.AGE_25_34,
        gender=Gender.FEMALE,
        verification_level=3,
        trust_score=0.85,
        created_at=datetime.utcnow() - timedelta(days=30),
    )


@pytest.fixture
def tokyo_hiker_intent():
    """Intent for Tokyo hiker (Apr 1-10)."""
    return ParsedTravelerIntent(
        raw_input="Tokyo hiking trip",
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
        pace_preference=PacePreference.MODERATE,
        traveling_solo=True,
        open_to_companions=True,
        preferred_group_size=2,
        confidence_score=0.9,
        ambiguities=[],
        clarification_questions=[],
    )


@pytest.fixture
def tokyo_adventurer_profile():
    """Profile for Tokyo adventurer (overlapping dates)."""
    return TravelerProfile(
        id=2,
        user_id=2,
        name="Bob",
        email="bob@example.com",
        age_range=AgeRange.AGE_25_34,
        gender=Gender.MALE,
        verification_level=2,
        trust_score=0.75,
        created_at=datetime.utcnow() - timedelta(days=60),
    )


@pytest.fixture
def tokyo_adventurer_intent():
    """Intent for Tokyo adventurer (Apr 5-12, overlaps with hiker)."""
    return ParsedTravelerIntent(
        raw_input="Tokyo adventure",
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
        activities=[ActivityCategory.HIKING, ActivityCategory.ADVENTURE_SPORTS, ActivityCategory.SIGHTSEEING],
        budget_tier=BudgetTier.MODERATE,
        pace_preference=PacePreference.FAST,
        traveling_solo=True,
        open_to_companions=True,
        confidence_score=0.85,
        ambiguities=[],
        clarification_questions=[],
    )


@pytest.fixture
def paris_traveler_profile():
    """Profile for Paris traveler (different destination)."""
    return TravelerProfile(
        id=3,
        user_id=3,
        name="Charlie",
        email="charlie@example.com",
        age_range=AgeRange.AGE_35_44,
        gender=Gender.NON_BINARY,
        verification_level=3,
        trust_score=0.9,
        created_at=datetime.utcnow() - timedelta(days=90),
    )


@pytest.fixture
def paris_traveler_intent():
    """Intent for Paris traveler."""
    return ParsedTravelerIntent(
        raw_input="Paris art trip",
        primary_destination="Paris",
        destination_stays=[
            DestinationStay(
                destination="Paris",
                country="France",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 7),
                nights=6,
                activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS],
                is_flexible=False,
                flexibility_days=0,
            )
        ],
        activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS],
        budget_tier=BudgetTier.COMFORTABLE,
        pace_preference=PacePreference.RELAXED,
        traveling_solo=True,
        open_to_companions=True,
        confidence_score=0.9,
        ambiguities=[],
        clarification_questions=[],
    )


class TestDeterministicFilters:
    """Test deterministic filtering logic."""

    def test_same_destination_match(self, tokyo_hiker_intent, tokyo_adventurer_intent):
        """Test destination matching."""
        assert DeterministicFilters.same_destination(tokyo_hiker_intent, tokyo_adventurer_intent)

    def test_different_destination_no_match(self, tokyo_hiker_intent, paris_traveler_intent):
        """Test destination mismatch."""
        assert not DeterministicFilters.same_destination(tokyo_hiker_intent, paris_traveler_intent)

    def test_destination_case_insensitive(self, tokyo_hiker_intent):
        """Test destination matching is case-insensitive."""
        intent_upper = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="TOKYO",
            destination_stays=[],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        assert DeterministicFilters.same_destination(tokyo_hiker_intent, intent_upper)

    def test_overlapping_dates_full_overlap(self):
        """Test dates with full overlap."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 10),
                    nights=9,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 10),
                    nights=9,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        has_overlap, overlap_days = DeterministicFilters.overlapping_dates(intent_a, intent_b)
        assert has_overlap
        assert overlap_days == 10  # Inclusive

    def test_overlapping_dates_partial_overlap(self, tokyo_hiker_intent, tokyo_adventurer_intent):
        """Test dates with partial overlap."""
        has_overlap, overlap_days = DeterministicFilters.overlapping_dates(
            tokyo_hiker_intent, tokyo_adventurer_intent
        )
        assert has_overlap
        assert overlap_days == 6  # Apr 5-10

    def test_overlapping_dates_no_overlap(self):
        """Test dates with no overlap."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 5),
                    nights=4,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 10),
                    end_date=date(2024, 4, 15),
                    nights=5,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        has_overlap, overlap_days = DeterministicFilters.overlapping_dates(intent_a, intent_b)
        assert not has_overlap
        assert overlap_days == 0

    def test_age_compatible_same_range(self, tokyo_hiker_profile, tokyo_adventurer_profile):
        """Test age compatibility with same range."""
        assert DeterministicFilters.age_compatible(tokyo_hiker_profile, tokyo_adventurer_profile)

    def test_age_compatible_adjacent_ranges(self):
        """Test age compatibility with adjacent ranges."""
        profile_a = TravelerProfile(
            id=1,
            user_id=1,
            name="Alice",
            email="alice@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.FEMALE,
            verification_level=3,
            trust_score=0.85,
        )
        profile_b = TravelerProfile(
            id=2,
            user_id=2,
            name="Bob",
            email="bob@example.com",
            age_range=AgeRange.AGE_35_44,
            gender=Gender.MALE,
            verification_level=2,
            trust_score=0.75,
        )

        # Non-strict allows adjacent
        assert DeterministicFilters.age_compatible(profile_a, profile_b, strict=False)

        # Strict requires exact match
        assert not DeterministicFilters.age_compatible(profile_a, profile_b, strict=True)

    def test_age_incompatible_far_apart(self):
        """Test age incompatibility with distant ranges."""
        profile_a = TravelerProfile(
            id=1,
            user_id=1,
            name="Alice",
            email="alice@example.com",
            age_range=AgeRange.UNDER_25,
            gender=Gender.FEMALE,
            verification_level=3,
            trust_score=0.85,
        )
        profile_b = TravelerProfile(
            id=2,
            user_id=2,
            name="Bob",
            email="bob@example.com",
            age_range=AgeRange.OVER_55,
            gender=Gender.MALE,
            verification_level=2,
            trust_score=0.75,
        )

        assert not DeterministicFilters.age_compatible(profile_a, profile_b, strict=False)

    def test_safety_compatible_verified_profiles(self, tokyo_hiker_profile, tokyo_adventurer_profile):
        """Test safety compatibility with verified profiles."""
        is_safe, flags = DeterministicFilters.safety_compatible(tokyo_hiker_profile, tokyo_adventurer_profile)
        assert is_safe
        assert SafetyFlag.UNVERIFIED_PROFILE not in flags

    def test_safety_flags_unverified(self):
        """Test safety flags for unverified profiles."""
        profile_a = TravelerProfile(
            id=1,
            user_id=1,
            name="Alice",
            email="alice@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.FEMALE,
            verification_level=0,  # Unverified
            trust_score=0.85,
        )
        profile_b = TravelerProfile(
            id=2,
            user_id=2,
            name="Bob",
            email="bob@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.MALE,
            verification_level=3,
            trust_score=0.75,
        )

        is_safe, flags = DeterministicFilters.safety_compatible(profile_a, profile_b)
        assert is_safe  # Still allow match
        assert SafetyFlag.UNVERIFIED_PROFILE in flags

    def test_safety_flags_low_trust(self):
        """Test safety flags for low trust scores."""
        profile_a = TravelerProfile(
            id=1,
            user_id=1,
            name="Alice",
            email="alice@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.FEMALE,
            verification_level=3,
            trust_score=0.3,  # Low trust
        )
        profile_b = TravelerProfile(
            id=2,
            user_id=2,
            name="Bob",
            email="bob@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.MALE,
            verification_level=3,
            trust_score=0.85,
        )

        is_safe, flags = DeterministicFilters.safety_compatible(profile_a, profile_b)
        assert is_safe
        assert SafetyFlag.LOW_TRUST_SCORE in flags


class TestSemanticScorer:
    """Test semantic compatibility scoring."""

    def test_activity_similarity_perfect_match(self):
        """Test activity similarity with identical activities."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR, ActivityCategory.MUSEUMS],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR, ActivityCategory.MUSEUMS],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        similarity, shared = SemanticScorer.activity_similarity(intent_a, intent_b)
        assert similarity == 1.0
        assert len(shared) == 3

    def test_activity_similarity_partial_overlap(self):
        """Test activity similarity with partial overlap."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR, ActivityCategory.MUSEUMS],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        similarity, shared = SemanticScorer.activity_similarity(intent_a, intent_b)
        # Jaccard: intersection=2, union=3, similarity=2/3=0.667
        assert abs(similarity - 0.667) < 0.01
        assert len(shared) == 2

    def test_activity_similarity_no_overlap(self):
        """Test activity similarity with no overlap."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.ADVENTURE_SPORTS],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        similarity, shared = SemanticScorer.activity_similarity(intent_a, intent_b)
        assert similarity == 0.0
        assert len(shared) == 0

    def test_budget_compatibility_same_tier(self):
        """Test budget compatibility with same tier."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score = SemanticScorer.budget_compatibility(intent_a, intent_b)
        assert score == 1.0

    def test_budget_compatibility_adjacent_tiers(self):
        """Test budget compatibility with adjacent tiers."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.BUDGET,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score = SemanticScorer.budget_compatibility(intent_a, intent_b)
        assert score == 0.75  # 1 tier apart

    def test_pace_compatibility_same_pace(self):
        """Test pace compatibility with same preference."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score = SemanticScorer.pace_compatibility(intent_a, intent_b)
        assert score == 1.0

    def test_pace_compatibility_different_pace(self):
        """Test pace compatibility with different preferences."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            pace_preference=PacePreference.RELAXED,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            pace_preference=PacePreference.FAST,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score = SemanticScorer.pace_compatibility(intent_a, intent_b)
        assert score == 0.5  # 2 steps apart

    def test_social_compatibility_solo_open(self):
        """Test social compatibility for solo travelers open to companions."""
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score = SemanticScorer.social_compatibility(intent_a, intent_b)
        assert score == 1.0


class TestTravelerMatcher:
    """Test full matching workflow."""

    def test_high_compatibility_match(
        self,
        tokyo_hiker_profile,
        tokyo_hiker_intent,
        tokyo_adventurer_profile,
        tokyo_adventurer_intent,
    ):
        """Test matching between highly compatible travelers."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        match_score = matcher.calculate_match(
            tokyo_hiker_profile,
            tokyo_hiker_intent,
            tokyo_adventurer_profile,
            tokyo_adventurer_intent,
        )

        assert match_score is not None
        assert match_score.overall_score >= 0.6  # Should be reasonably high
        assert match_score.destination_score == 1.0
        assert match_score.date_overlap_score > 0.5
        assert MatchReason.SAME_DESTINATION in match_score.top_reasons
        assert MatchReason.OVERLAPPING_DATES in match_score.top_reasons
        assert match_score.confidence >= 0.7

    def test_different_destinations_no_match(
        self,
        tokyo_hiker_profile,
        tokyo_hiker_intent,
        paris_traveler_profile,
        paris_traveler_intent,
    ):
        """Test that different destinations result in no match."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        match_score = matcher.calculate_match(
            tokyo_hiker_profile,
            tokyo_hiker_intent,
            paris_traveler_profile,
            paris_traveler_intent,
        )

        assert match_score is None  # Filtered out

    def test_confidence_decreases_with_missing_data(
        self,
        tokyo_hiker_profile,
        tokyo_adventurer_profile,
    ):
        """Test that confidence decreases when data is missing."""
        # Intent with missing data
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],  # No dates
            activities=[],  # No activities
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.5,  # Low confidence
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        matcher = TravelerMatcher(use_llm_reranker=False)
        match_score = matcher.calculate_match(
            tokyo_hiker_profile,
            intent_a,
            tokyo_adventurer_profile,
            intent_b,
        )

        assert match_score is not None
        assert match_score.confidence < 0.7  # Lower confidence due to missing data

    def test_safety_flags_included(self):
        """Test that safety flags are included in match score."""
        profile_a = TravelerProfile(
            id=1,
            user_id=1,
            name="Alice",
            email="alice@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.FEMALE,
            verification_level=0,  # Unverified
            trust_score=0.4,  # Low trust
        )
        profile_b = TravelerProfile(
            id=2,
            user_id=2,
            name="Bob",
            email="bob@example.com",
            age_range=AgeRange.AGE_25_34,
            gender=Gender.MALE,
            verification_level=3,
            trust_score=0.85,
        )
        intent_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 10),
                    nights=9,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[ActivityCategory.HIKING],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )
        intent_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 10),
                    nights=9,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[ActivityCategory.HIKING],
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        matcher = TravelerMatcher(use_llm_reranker=False)
        match_score = matcher.calculate_match(profile_a, intent_a, profile_b, intent_b)

        assert match_score is not None
        assert SafetyFlag.UNVERIFIED_PROFILE in match_score.safety_flags
        assert SafetyFlag.LOW_TRUST_SCORE in match_score.safety_flags
