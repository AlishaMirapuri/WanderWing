"""
Integration tests for end-to-end traveler matching workflow.

Tests cover:
- Intent parsing → Matching → Results
- API route integration
- Database persistence (when available)
- Full workflow from raw input to match results
"""

from datetime import date

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
    MatchReason,
    SafetyFlag,
    TravelerMatcher,
)


@pytest.fixture
def sample_users():
    """Create 6 sample users matching SAMPLE_MATCHES.md."""
    users = {
        "alice": {
            "profile": TravelerProfile(
                id=1,
                user_id=1,
                name="Alice",
                email="alice@example.com",
                age_range=AgeRange.AGE_25_34,
                gender=Gender.FEMALE,
                verification_level=3,
                trust_score=0.85,
            ),
            "intent": ParsedTravelerIntent(
                raw_input="Tokyo hiking and food tours",
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
                confidence_score=0.9,
                ambiguities=[],
                clarification_questions=[],
            ),
        },
        "bob": {
            "profile": TravelerProfile(
                id=2,
                user_id=2,
                name="Bob",
                email="bob@example.com",
                age_range=AgeRange.AGE_25_34,
                gender=Gender.MALE,
                verification_level=2,
                trust_score=0.75,
            ),
            "intent": ParsedTravelerIntent(
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
            ),
        },
        "charlie": {
            "profile": TravelerProfile(
                id=3,
                user_id=3,
                name="Charlie",
                email="charlie@example.com",
                age_range=AgeRange.AGE_35_44,
                gender=Gender.NON_BINARY,
                verification_level=3,
                trust_score=0.90,
            ),
            "intent": ParsedTravelerIntent(
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
                activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS, ActivityCategory.FOOD_TOUR],
                budget_tier=BudgetTier.COMFORTABLE,
                pace_preference=PacePreference.RELAXED,
                traveling_solo=True,
                open_to_companions=True,
                confidence_score=0.9,
                ambiguities=[],
                clarification_questions=[],
            ),
        },
        "diana": {
            "profile": TravelerProfile(
                id=4,
                user_id=4,
                name="Diana",
                email="diana@example.com",
                age_range=AgeRange.UNDER_25,
                gender=Gender.FEMALE,
                verification_level=1,
                trust_score=0.60,
            ),
            "intent": ParsedTravelerIntent(
                raw_input="Tokyo budget backpacking",
                primary_destination="Tokyo",
                destination_stays=[
                    DestinationStay(
                        destination="Tokyo",
                        country="Japan",
                        start_date=date(2024, 4, 3),
                        end_date=date(2024, 4, 15),
                        nights=12,
                        activities=[ActivityCategory.SIGHTSEEING, ActivityCategory.LOCAL_EXPERIENCES],
                        is_flexible=False,
                        flexibility_days=0,
                    )
                ],
                activities=[ActivityCategory.SIGHTSEEING, ActivityCategory.LOCAL_EXPERIENCES, ActivityCategory.FOOD_TOUR],
                budget_tier=BudgetTier.BUDGET,
                pace_preference=PacePreference.FAST,
                traveling_solo=True,
                open_to_companions=True,
                confidence_score=0.9,
                ambiguities=[],
                clarification_questions=[],
            ),
        },
        "erik": {
            "profile": TravelerProfile(
                id=5,
                user_id=5,
                name="Erik",
                email="erik@example.com",
                age_range=AgeRange.AGE_45_54,
                gender=Gender.MALE,
                verification_level=4,
                trust_score=0.95,
            ),
            "intent": ParsedTravelerIntent(
                raw_input="Tokyo cultural exploration",
                primary_destination="Tokyo",
                destination_stays=[
                    DestinationStay(
                        destination="Tokyo",
                        country="Japan",
                        start_date=date(2024, 4, 1),
                        end_date=date(2024, 4, 10),
                        nights=9,
                        activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS],
                        is_flexible=False,
                        flexibility_days=0,
                    )
                ],
                activities=[ActivityCategory.MUSEUMS, ActivityCategory.CULTURAL_EVENTS, ActivityCategory.SIGHTSEEING, ActivityCategory.FOOD_TOUR],
                budget_tier=BudgetTier.COMFORTABLE,
                pace_preference=PacePreference.RELAXED,
                traveling_solo=True,
                open_to_companions=True,
                confidence_score=0.9,
                ambiguities=[],
                clarification_questions=[],
            ),
        },
        "fiona": {
            "profile": TravelerProfile(
                id=6,
                user_id=6,
                name="Fiona",
                email="fiona@example.com",
                age_range=AgeRange.AGE_35_44,
                gender=Gender.FEMALE,
                verification_level=3,
                trust_score=0.85,
            ),
            "intent": ParsedTravelerIntent(
                raw_input="Tokyo wellness retreat",
                primary_destination="Tokyo",
                destination_stays=[
                    DestinationStay(
                        destination="Tokyo",
                        country="Japan",
                        start_date=date(2024, 4, 8),
                        end_date=date(2024, 4, 14),
                        nights=6,
                        activities=[ActivityCategory.WELLNESS, ActivityCategory.FOOD_TOUR],
                        is_flexible=False,
                        flexibility_days=0,
                    )
                ],
                activities=[ActivityCategory.WELLNESS, ActivityCategory.FOOD_TOUR, ActivityCategory.LOCAL_EXPERIENCES],
                budget_tier=BudgetTier.COMFORTABLE,
                pace_preference=PacePreference.RELAXED,
                traveling_solo=True,
                open_to_companions=True,
                confidence_score=0.9,
                ambiguities=[],
                clarification_questions=[],
            ),
        },
    }
    return users


class TestMatchingWorkflow:
    """Test complete matching workflow."""

    def test_alice_bob_high_compatibility(self, sample_users):
        """Test Alice ↔ Bob match (expected score ~0.74)."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        bob = sample_users["bob"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            bob["profile"],
            bob["intent"],
        )

        # Verify match exists
        assert match_score is not None

        # Verify overall score
        assert 0.70 <= match_score.overall_score <= 0.80

        # Verify component scores
        assert match_score.destination_score == 1.0
        assert match_score.date_overlap_score >= 0.6
        assert match_score.budget_compatibility == 1.0

        # Verify top reasons
        assert MatchReason.SAME_DESTINATION in match_score.top_reasons
        assert MatchReason.OVERLAPPING_DATES in match_score.top_reasons

        # Verify confidence
        assert match_score.confidence >= 0.65

        # Verify no safety flags
        assert len(match_score.safety_flags) == 0

    def test_alice_charlie_no_match_different_destinations(self, sample_users):
        """Test Alice ↔ Charlie (different destinations, should be filtered)."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        charlie = sample_users["charlie"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            charlie["profile"],
            charlie["intent"],
        )

        # Should be filtered out
        assert match_score is None

    def test_alice_diana_safety_flags(self, sample_users):
        """Test Alice ↔ Diana (should have safety flags)."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        diana = sample_users["diana"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            diana["profile"],
            diana["intent"],
        )

        # Match should exist
        assert match_score is not None

        # Should have safety flags
        assert SafetyFlag.UNVERIFIED_PROFILE in match_score.safety_flags
        assert SafetyFlag.LOW_TRUST_SCORE in match_score.safety_flags

        # Confidence should be reduced
        assert match_score.confidence < 0.65

    def test_alice_erik_perfect_date_overlap(self, sample_users):
        """Test Alice ↔ Erik (perfect date overlap)."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        erik = sample_users["erik"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            erik["profile"],
            erik["intent"],
        )

        assert match_score is not None

        # Perfect date overlap
        assert match_score.date_overlap_score == 1.0

        # But age compatibility reduced
        assert match_score.age_compatibility < 0.8

        # Overall still good
        assert match_score.overall_score >= 0.60

    def test_bob_diana_pace_alignment(self, sample_users):
        """Test Bob ↔ Diana (both fast pace)."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        bob = sample_users["bob"]
        diana = sample_users["diana"]

        match_score = matcher.calculate_match(
            bob["profile"],
            bob["intent"],
            diana["profile"],
            diana["intent"],
        )

        assert match_score is not None

        # Perfect pace compatibility
        assert match_score.pace_compatibility == 1.0

        # But has safety flags
        assert len(match_score.safety_flags) > 0

    def test_erik_fiona_complementary_activities(self, sample_users):
        """Test Erik ↔ Fiona (relaxed pace, different activities)."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        erik = sample_users["erik"]
        fiona = sample_users["fiona"]

        match_score = matcher.calculate_match(
            erik["profile"],
            erik["intent"],
            fiona["profile"],
            fiona["intent"],
        )

        assert match_score is not None

        # Same pace (both relaxed)
        assert match_score.pace_compatibility == 1.0

        # Age compatible
        assert match_score.age_compatibility >= 0.8

        # Overall good match
        assert match_score.overall_score >= 0.60

    def test_match_all_tokyo_travelers(self, sample_users):
        """Test finding all matches for Tokyo travelers."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        tokyo_travelers = ["alice", "bob", "diana", "erik", "fiona"]
        alice = sample_users["alice"]

        matches = []
        for traveler_name in tokyo_travelers:
            if traveler_name == "alice":
                continue

            traveler = sample_users[traveler_name]
            match_score = matcher.calculate_match(
                alice["profile"],
                alice["intent"],
                traveler["profile"],
                traveler["intent"],
            )

            if match_score:
                matches.append((traveler_name, match_score.overall_score))

        # Alice should match with all Tokyo travelers
        assert len(matches) == 4

        # Verify matches in expected score order (roughly)
        match_dict = dict(matches)
        assert "bob" in match_dict
        assert "diana" in match_dict
        assert "erik" in match_dict
        assert "fiona" in match_dict

        # Bob should be highest match
        assert match_dict["bob"] >= 0.70

    def test_no_one_matches_charlie(self, sample_users):
        """Test that Charlie (Paris) matches with no Tokyo travelers."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        tokyo_travelers = ["alice", "bob", "diana", "erik", "fiona"]
        charlie = sample_users["charlie"]

        matches = []
        for traveler_name in tokyo_travelers:
            traveler = sample_users[traveler_name]
            match_score = matcher.calculate_match(
                charlie["profile"],
                charlie["intent"],
                traveler["profile"],
                traveler["intent"],
            )

            if match_score:
                matches.append(traveler_name)

        # Charlie should match with no one (different destination)
        assert len(matches) == 0

    def test_symmetric_matching(self, sample_users):
        """Test that A→B score equals B→A score."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        bob = sample_users["bob"]

        # Calculate Alice → Bob
        score_ab = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            bob["profile"],
            bob["intent"],
        )

        # Calculate Bob → Alice
        score_ba = matcher.calculate_match(
            bob["profile"],
            bob["intent"],
            alice["profile"],
            alice["intent"],
        )

        # Scores should be identical (symmetric)
        assert abs(score_ab.overall_score - score_ba.overall_score) < 0.01
        assert abs(score_ab.activity_similarity - score_ba.activity_similarity) < 0.01
        assert abs(score_ab.budget_compatibility - score_ba.budget_compatibility) < 0.01

    def test_match_confidence_with_complete_data(self, sample_users):
        """Test that confidence is high when all data is present."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        bob = sample_users["bob"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            bob["profile"],
            bob["intent"],
        )

        # High confidence with complete, verified data
        assert match_score.confidence >= 0.65

    def test_minimum_overlap_filter(self, sample_users):
        """Test that min_overlap_days filter works."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        fiona = sample_users["fiona"]

        # Alice (Apr 1-10) and Fiona (Apr 8-14) have 3 days overlap

        # With min_overlap_days=1, should match
        match_1 = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            fiona["profile"],
            fiona["intent"],
            min_overlap_days=1,
        )
        assert match_1 is not None

        # With min_overlap_days=5, should NOT match
        match_5 = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            fiona["profile"],
            fiona["intent"],
            min_overlap_days=5,
        )
        assert match_5 is None


class TestMatchScoreInspection:
    """Test that match scores are inspectable and debuggable."""

    def test_component_scores_sum_to_overall(self, sample_users):
        """Test that component scores contribute to overall score."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        bob = sample_users["bob"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            bob["profile"],
            bob["intent"],
        )

        # Manual calculation (weighted average)
        weights = {
            'destination': 0.20,
            'dates': 0.20,
            'activities': 0.20,
            'budget': 0.15,
            'pace': 0.10,
            'social': 0.10,
            'age': 0.05,
        }

        calculated_score = (
            match_score.destination_score * weights['destination'] +
            match_score.date_overlap_score * weights['dates'] +
            match_score.activity_similarity * weights['activities'] +
            match_score.budget_compatibility * weights['budget'] +
            match_score.pace_compatibility * weights['pace'] +
            match_score.social_compatibility * weights['social'] +
            match_score.age_compatibility * weights['age']
        )

        # Should match within rounding
        assert abs(match_score.overall_score - calculated_score) < 0.01

    def test_reasons_reflect_high_scores(self, sample_users):
        """Test that top_reasons include dimensions with high scores."""
        matcher = TravelerMatcher(use_llm_reranker=False)

        alice = sample_users["alice"]
        bob = sample_users["bob"]

        match_score = matcher.calculate_match(
            alice["profile"],
            alice["intent"],
            bob["profile"],
            bob["intent"],
        )

        # If budget_compatibility is 1.0, should be in reasons
        if match_score.budget_compatibility >= 0.7:
            assert MatchReason.COMPATIBLE_BUDGET in match_score.top_reasons

        # If destination_score is 1.0, should be in reasons
        if match_score.destination_score >= 0.7:
            assert MatchReason.SAME_DESTINATION in match_score.top_reasons
