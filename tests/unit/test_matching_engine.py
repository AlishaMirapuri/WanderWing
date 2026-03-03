"""
Comprehensive unit tests for MatchingEngine.

Tests hybrid matching algorithm, dimension scoring, LLM integration, and edge cases.
"""

import json
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wanderwing.llm.client import LLMResponse
from wanderwing.schemas.match_enhanced import (
    CompatibilityDimension,
    DimensionScore,
    MatchCandidate,
    MatchReason,
)
from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    DestinationStay,
    ParsedTravelerIntent,
    PacePreference,
)
from wanderwing.services.matching_engine import MatchingEngine


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    with patch("wanderwing.services.matching_engine.get_llm_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def matching_engine(mock_llm_client):
    """Create MatchingEngine instance for testing."""
    return MatchingEngine()


@pytest.fixture
def tokyo_traveler_a():
    """Create a typical Tokyo traveler (hiking + food)."""
    return ParsedTravelerIntent(
        raw_input="Tokyo hiking and food trip",
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


@pytest.fixture
def tokyo_traveler_b():
    """Create another Tokyo traveler with overlapping interests."""
    return ParsedTravelerIntent(
        raw_input="Tokyo adventure trip",
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
        pace_preference=PacePreference.MODERATE,
        traveling_solo=True,
        open_to_companions=True,
        preferred_group_size=2,
        confidence_score=0.85,
        ambiguities=[],
        clarification_questions=[],
    )


@pytest.fixture
def paris_traveler():
    """Create a Paris traveler (incompatible destination)."""
    return ParsedTravelerIntent(
        raw_input="Paris cultural trip",
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


@pytest.fixture
def valid_llm_response():
    """Valid LLM response for match explanation."""
    return {
        "similarity_score": 0.85,
        "summary": "Excellent match for travel companions. Both are visiting Tokyo in early April with shared interests in hiking and outdoor activities. Their moderate budgets and solo travel preferences align well.",
        "why_great_match": [
            "6 days of perfect date overlap (April 5-10)",
            "Shared passion for hiking and outdoor activities",
            "Similar moderate budget range ($100-150/day)",
            "Both solo travelers open to meeting companions",
            "Compatible travel pace preferences",
        ],
        "shared_interests": ["hiking", "sightseeing", "outdoor_activities", "japanese_culture"],
        "complementary_traits": [
            "Traveler A has food tour experience, Traveler B is interested in local cuisine",
            "Traveler B's adventure sports interest adds variety to hiking plans",
        ],
        "potential_concerns": [
            "Slightly different activity focus (food vs adventure sports)",
        ],
        "conversation_starters": [
            "Want to hike Mt. Fuji together during our overlapping dates?",
            "I'm planning a day trip to Hakone - interested in joining?",
            "Have you found any good ramen spots in Tokyo yet?",
        ],
    }


class TestMatchingEngineSuccess:
    """Test successful matching scenarios."""

    @pytest.mark.asyncio
    async def test_perfect_match_high_score(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client, valid_llm_response
    ):
        """Test perfect match with high compatibility score."""
        # Setup mock
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=800,
            cost_usd=0.016,
        )

        # Calculate match
        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=tokyo_traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
            use_llm=True,
        )

        # Assertions
        assert result is not None
        assert isinstance(result, MatchCandidate)
        assert result.match_explanation.overall_score >= 0.7  # Should be high
        assert result.destination == "Tokyo"
        assert result.overlapping_days == 6  # April 5-10
        assert MatchReason.SAME_DESTINATION in result.match_explanation.primary_reasons
        assert MatchReason.OVERLAPPING_DATES in result.match_explanation.primary_reasons

    @pytest.mark.asyncio
    async def test_dimension_scores_populated(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client, valid_llm_response
    ):
        """Test that all dimension scores are calculated."""
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=800,
            cost_usd=0.016,
        )

        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=tokyo_traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
        )

        # Check dimension scores exist
        dimension_scores = result.match_explanation.dimension_scores
        assert len(dimension_scores) >= 5  # At least 5 dimensions

        # Check key dimensions are present
        dimensions = {ds.dimension for ds in dimension_scores}
        assert CompatibilityDimension.DESTINATION in dimensions
        assert CompatibilityDimension.DATES in dimensions
        assert CompatibilityDimension.ACTIVITIES in dimensions
        assert CompatibilityDimension.BUDGET in dimensions

        # Check each score has explanation
        for ds in dimension_scores:
            assert isinstance(ds, DimensionScore)
            assert 0.0 <= ds.score <= 1.0
            assert len(ds.explanation) > 0

    @pytest.mark.asyncio
    async def test_llm_insights_included(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client, valid_llm_response
    ):
        """Test that LLM insights are included in match explanation."""
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=800,
            cost_usd=0.016,
        )

        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=tokyo_traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
        )

        explanation = result.match_explanation
        assert explanation.llm_summary == valid_llm_response["summary"]
        assert explanation.shared_interests == valid_llm_response["shared_interests"]
        assert explanation.why_great_match == valid_llm_response["why_great_match"]
        assert explanation.conversation_starters == valid_llm_response["conversation_starters"]
        assert explanation.complementary_traits == valid_llm_response["complementary_traits"]
        assert explanation.potential_concerns == valid_llm_response["potential_concerns"]

    @pytest.mark.asyncio
    async def test_hybrid_scoring_calculation(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client
    ):
        """Test hybrid scoring combines LLM and rule-based scores correctly."""
        # Mock LLM to return specific similarity score
        llm_response = {
            "similarity_score": 0.9,
            "summary": "Great match",
            "why_great_match": ["Reason 1"],
            "shared_interests": [],
            "complementary_traits": [],
            "potential_concerns": [],
            "conversation_starters": [],
        }
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(llm_response),
            model="gpt-4-turbo",
            tokens_used=800,
            cost_usd=0.016,
        )

        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=tokyo_traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
        )

        # Verify hybrid calculation
        explanation = result.match_explanation
        assert explanation.hybrid_weight_llm == 0.6
        assert explanation.hybrid_weight_rules == 0.4
        assert explanation.llm_similarity_score == 0.9

        # Overall score should be weighted average
        expected_overall = (0.6 * 0.9) + (0.4 * explanation.rule_based_score)
        assert abs(explanation.overall_score - expected_overall) < 0.01


class TestMatchingEngineFiltering:
    """Test filtering and rejection scenarios."""

    @pytest.mark.asyncio
    async def test_different_destinations_rejected(
        self, matching_engine, tokyo_traveler_a, paris_traveler
    ):
        """Test that travelers with different destinations are rejected."""
        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=paris_traveler,
            traveler_a_id=1,
            traveler_b_id=2,
        )

        # Should be rejected by basic filters
        assert result is None

    @pytest.mark.asyncio
    async def test_no_date_overlap_rejected(self, matching_engine, tokyo_traveler_a):
        """Test that travelers with no date overlap are rejected."""
        # Create traveler with non-overlapping dates
        non_overlapping = ParsedTravelerIntent(
            raw_input="Tokyo trip later",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 5, 1),  # After traveler_a ends
                    end_date=date(2024, 5, 7),
                    nights=6,
                    activities=[ActivityCategory.HIKING],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[ActivityCategory.HIKING],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=non_overlapping,
            traveler_a_id=1,
            traveler_b_id=2,
        )

        # Should be rejected by date filter
        assert result is None


class TestDimensionScoring:
    """Test individual dimension scoring functions."""

    def test_destination_score_exact_match(self, matching_engine, tokyo_traveler_a, tokyo_traveler_b):
        """Test destination scoring with exact match."""
        score, explanation, factors = matching_engine._score_destination(
            tokyo_traveler_a, tokyo_traveler_b
        )

        assert score == 1.0
        assert "Tokyo" in explanation
        assert "Tokyo" in factors

    def test_date_overlap_calculation(self, matching_engine, tokyo_traveler_a, tokyo_traveler_b):
        """Test date overlap scoring."""
        score, explanation, factors = matching_engine._score_dates(tokyo_traveler_a, tokyo_traveler_b)

        # April 5-10 overlap = 6 days
        assert score > 0.5  # Should have positive overlap
        assert "6 days" in explanation or "overlap" in explanation.lower()

    def test_activity_similarity_jaccard(self, matching_engine):
        """Test activity similarity using Jaccard index."""
        # Travelers with partial activity overlap
        traveler_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR, ActivityCategory.MUSEUMS],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        traveler_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[ActivityCategory.HIKING, ActivityCategory.FOOD_TOUR],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score, explanation, factors = matching_engine._score_activities(traveler_a, traveler_b)

        # Intersection: 2 (hiking, food_tour)
        # Union: 3 (hiking, food_tour, museums)
        # Jaccard: 2/3 = 0.667
        assert abs(score - 0.667) < 0.01
        assert len(factors) == 2  # 2 shared activities

    def test_budget_compatibility_same_tier(self, matching_engine):
        """Test budget scoring with same tier."""
        traveler_a = ParsedTravelerIntent(
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

        traveler_b = ParsedTravelerIntent(
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

        score, explanation, factors = matching_engine._score_budget(traveler_a, traveler_b)

        assert score == 1.0
        assert "moderate" in explanation.lower()

    def test_budget_compatibility_different_tiers(self, matching_engine):
        """Test budget scoring with different tiers."""
        traveler_a = ParsedTravelerIntent(
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

        traveler_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.LUXURY,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score, explanation, factors = matching_engine._score_budget(traveler_a, traveler_b)

        # Budget (1) to Luxury (4) = distance of 3
        # Score = 1.0 - (3 * 0.25) = 0.25
        assert abs(score - 0.25) < 0.01

    def test_pace_compatibility_same_pace(self, matching_engine):
        """Test pace scoring with same preference."""
        traveler_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        traveler_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        score, explanation, factors = matching_engine._score_pace(traveler_a, traveler_b)

        assert score == 1.0
        assert "moderate" in explanation.lower()

    def test_social_compatibility_solo_open(self, matching_engine):
        """Test social scoring for solo travelers open to companions."""
        traveler_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        traveler_b = ParsedTravelerIntent(
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

        score, explanation, factors = matching_engine._score_social(traveler_a, traveler_b)

        assert score == 1.0
        assert "solo" in explanation.lower()
        assert "companions" in explanation.lower()


class TestLLMIntegration:
    """Test LLM integration and error handling."""

    @pytest.mark.asyncio
    async def test_llm_malformed_json_fallback(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client
    ):
        """Test fallback when LLM returns malformed JSON."""
        # Mock malformed response
        mock_llm_client.complete.return_value = LLMResponse(
            content='{"similarity_score": invalid json',
            model="gpt-4-turbo",
            tokens_used=200,
            cost_usd=0.004,
        )

        similarity, insights = await matching_engine._calculate_llm_similarity(
            tokyo_traveler_a, tokyo_traveler_b
        )

        # Should fall back to default
        assert similarity == 0.5
        assert "Unable to generate detailed insights" in insights["summary"]

    @pytest.mark.asyncio
    async def test_llm_exception_handling(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client
    ):
        """Test exception handling in LLM similarity calculation."""
        # Mock exception
        mock_llm_client.complete.side_effect = Exception("API error")

        similarity, insights = await matching_engine._calculate_llm_similarity(
            tokyo_traveler_a, tokyo_traveler_b
        )

        # Should fall back gracefully
        assert similarity == 0.5
        assert "Unable to generate detailed insights" in insights["summary"]

    @pytest.mark.asyncio
    async def test_matching_without_llm(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client
    ):
        """Test matching works without LLM (rule-based only)."""
        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=tokyo_traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
            use_llm=False,  # Disable LLM
        )

        # Should still produce a match using rule-based scoring
        assert result is not None
        assert result.match_explanation.llm_similarity_score == 0.5  # Default
        assert result.match_explanation.rule_based_score > 0
        assert mock_llm_client.complete.call_count == 0  # LLM not called


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_missing_destination_stays(self, matching_engine):
        """Test handling of travelers with no destination stays."""
        traveler_a = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],  # Empty
            activities=[ActivityCategory.HIKING],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.5,
            ambiguities=["No dates specified"],
            clarification_questions=[],
        )

        traveler_b = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[],  # Empty
            activities=[ActivityCategory.HIKING],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.5,
            ambiguities=["No dates specified"],
            clarification_questions=[],
        )

        # Should handle gracefully with default scores
        result = await matching_engine.calculate_match(
            traveler_a=traveler_a,
            traveler_b=traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
            use_llm=False,
        )

        assert result is not None
        # Date score should be 0.5 (unknown)
        date_scores = [
            ds for ds in result.match_explanation.dimension_scores
            if ds.dimension == CompatibilityDimension.DATES
        ]
        assert len(date_scores) == 1
        assert date_scores[0].score == 0.5

    @pytest.mark.asyncio
    async def test_no_activities_specified(self, matching_engine, tokyo_traveler_a):
        """Test handling of travelers with no activities."""
        traveler_no_activities = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=tokyo_traveler_a.destination_stays,
            activities=[],  # No activities
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.6,
            ambiguities=[],
            clarification_questions=[],
        )

        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=traveler_no_activities,
            traveler_a_id=1,
            traveler_b_id=2,
            use_llm=False,
        )

        # Should handle gracefully
        assert result is not None
        activity_scores = [
            ds for ds in result.match_explanation.dimension_scores
            if ds.dimension == CompatibilityDimension.ACTIVITIES
        ]
        assert len(activity_scores) == 1
        assert activity_scores[0].score == 0.5  # Default for incomplete info

    @pytest.mark.asyncio
    async def test_overlapping_days_calculation_edge_cases(self, matching_engine):
        """Test overlapping days calculation for various scenarios."""
        # Exact overlap
        traveler_a = ParsedTravelerIntent(
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
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        traveler_b = ParsedTravelerIntent(
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
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        overlap = matching_engine._calculate_overlapping_days(traveler_a, traveler_b)
        assert overlap == 10  # Exact same dates

        # Partial overlap
        traveler_c = ParsedTravelerIntent(
            raw_input="test",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 5),
                    end_date=date(2024, 4, 15),
                    nights=10,
                    activities=[],
                    is_flexible=False,
                    flexibility_days=0,
                )
            ],
            activities=[],
            budget_tier=BudgetTier.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
            confidence_score=0.9,
            ambiguities=[],
            clarification_questions=[],
        )

        overlap = matching_engine._calculate_overlapping_days(traveler_a, traveler_c)
        assert overlap == 6  # April 5-10

    @pytest.mark.asyncio
    async def test_match_reasons_determined_correctly(
        self, matching_engine, tokyo_traveler_a, tokyo_traveler_b, mock_llm_client, valid_llm_response
    ):
        """Test that match reasons are determined based on high dimension scores."""
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(valid_llm_response),
            model="gpt-4-turbo",
            tokens_used=800,
            cost_usd=0.016,
        )

        result = await matching_engine.calculate_match(
            traveler_a=tokyo_traveler_a,
            traveler_b=tokyo_traveler_b,
            traveler_a_id=1,
            traveler_b_id=2,
        )

        reasons = result.match_explanation.primary_reasons
        assert len(reasons) >= 1
        assert len(reasons) <= 5  # Max 5 reasons

        # Should include destination (perfect match)
        assert MatchReason.SAME_DESTINATION in reasons
