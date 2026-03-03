"""
Unit tests for activity recommendation engine.

Tests filtering, scoring, and explanation generation logic.
"""

from datetime import datetime, timedelta

import pytest

from wanderwing.data.activity_repository import ActivityRepository
from wanderwing.schemas.activity import (
    Activity,
    ActivityTag,
    CostLevel,
    TimeOfDay,
)
from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    PacePreference,
    ParsedTravelerIntent,
)
from wanderwing.schemas.user import TravelerProfile, AgeRange
from wanderwing.services.activity_recommender import ActivityRecommender


# Test Fixtures


@pytest.fixture
def sample_activities():
    """Create sample activities for testing."""
    return [
        Activity(
            id="test-food-tour",
            name="Local Food Market Tour",
            description="Explore traditional food market with local guide",
            city="TestCity",
            tags=[ActivityTag.FOOD, ActivityTag.LOCAL_EXPERIENCE],
            cost_level=CostLevel.MODERATE,
            duration_hours=3.0,
            best_time=[TimeOfDay.MORNING],
            best_for=["food_tours", "local_experiences"],
            introvert_score=0.6,
            physical_intensity=0.3,
            cultural_depth=0.8,
            typical_rating=4.7,
            meeting_friendly=True,
        ),
        Activity(
            id="test-hiking",
            name="Mountain Hike",
            description="Challenging day hike with stunning views",
            city="TestCity",
            tags=[ActivityTag.OUTDOORS, ActivityTag.ADVENTURE],
            cost_level=CostLevel.BUDGET,
            duration_hours=6.0,
            best_time=[TimeOfDay.MORNING],
            best_for=["hiking", "adventure_sports"],
            introvert_score=0.7,
            physical_intensity=0.8,
            cultural_depth=0.3,
            typical_rating=4.9,
            meeting_friendly=True,
        ),
        Activity(
            id="test-museum",
            name="Art Museum",
            description="World-class art collection",
            city="TestCity",
            tags=[ActivityTag.CULTURE, ActivityTag.INTROVERT_FRIENDLY],
            cost_level=CostLevel.MODERATE,
            duration_hours=2.5,
            best_time=[TimeOfDay.AFTERNOON],
            best_for=["museums", "cultural_events"],
            introvert_score=0.8,
            physical_intensity=0.2,
            cultural_depth=0.9,
            typical_rating=4.6,
            meeting_friendly=True,
        ),
        Activity(
            id="test-expensive-tour",
            name="Luxury Wine Tasting",
            description="Premium wine experience",
            city="TestCity",
            tags=[ActivityTag.FOOD],
            cost_level=CostLevel.LUXURY,
            duration_hours=3.0,
            best_time=[TimeOfDay.EVENING],
            best_for=["food_tours"],
            introvert_score=0.6,
            physical_intensity=0.1,
            cultural_depth=0.7,
            typical_rating=4.8,
            meeting_friendly=True,
        ),
        Activity(
            id="test-not-meeting-friendly",
            name="Spa Day",
            description="Relaxing spa treatment",
            city="TestCity",
            tags=[ActivityTag.WELLNESS],
            cost_level=CostLevel.EXPENSIVE,
            duration_hours=2.0,
            best_time=[TimeOfDay.AFTERNOON],
            best_for=["wellness"],
            introvert_score=0.9,
            physical_intensity=0.1,
            cultural_depth=0.5,
            typical_rating=4.7,
            meeting_friendly=False,  # Not good for first meetup
        ),
        Activity(
            id="test-long-activity",
            name="Multi-Day Trek",
            description="3-day camping trek",
            city="TestCity",
            tags=[ActivityTag.OUTDOORS, ActivityTag.ADVENTURE],
            cost_level=CostLevel.EXPENSIVE,
            duration_hours=72.0,  # Too long for first meetup
            best_time=[TimeOfDay.MORNING],
            best_for=["hiking", "adventure_sports"],
            introvert_score=0.6,
            physical_intensity=0.9,
            cultural_depth=0.4,
            typical_rating=4.9,
            meeting_friendly=True,
        ),
    ]


@pytest.fixture
def mock_repository(sample_activities):
    """Create mock repository with test data."""

    class MockRepository(ActivityRepository):
        def __init__(self, activities):
            super().__init__()
            self.test_activities = activities

        def get_activities_for_city(self, city: str):
            return self.test_activities

    return MockRepository(sample_activities)


@pytest.fixture
def food_lovers_profiles():
    """Profiles for two food-loving travelers."""
    return [
        TravelerProfile(
            user_id="user1",
            age_range=AgeRange.AGE_25_34,
            verification_level=3,
            trust_score=0.85,
        ),
        TravelerProfile(
            user_id="user2",
            age_range=AgeRange.AGE_25_34,
            verification_level=2,
            trust_score=0.75,
        ),
    ]


@pytest.fixture
def food_lovers_intents():
    """Intents for two food-loving travelers."""
    today = datetime.now().date()
    return [
        ParsedTravelerIntent(
            primary_destination="TestCity",
            overall_start_date=today,
            overall_end_date=today + timedelta(days=7),
            activities=[ActivityCategory.FOOD_TOURS, ActivityCategory.SIGHTSEEING],
            budget_tier=BudgetTier.MODERATE,
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
        ),
        ParsedTravelerIntent(
            primary_destination="TestCity",
            overall_start_date=today + timedelta(days=2),
            overall_end_date=today + timedelta(days=9),
            activities=[ActivityCategory.FOOD_TOURS, ActivityCategory.LOCAL_EXPERIENCES],
            budget_tier=BudgetTier.MODERATE,
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
        ),
    ]


@pytest.fixture
def hikers_profiles():
    """Profiles for two hiking enthusiasts."""
    return [
        TravelerProfile(
            user_id="user3",
            age_range=AgeRange.AGE_25_34,
            verification_level=3,
            trust_score=0.90,
        ),
        TravelerProfile(
            user_id="user4",
            age_range=AgeRange.AGE_25_34,
            verification_level=3,
            trust_score=0.88,
        ),
    ]


@pytest.fixture
def hikers_intents():
    """Intents for two hiking enthusiasts."""
    today = datetime.now().date()
    return [
        ParsedTravelerIntent(
            primary_destination="TestCity",
            overall_start_date=today,
            overall_end_date=today + timedelta(days=5),
            activities=[ActivityCategory.HIKING, ActivityCategory.ADVENTURE_SPORTS],
            budget_tier=BudgetTier.BUDGET,
            pace_preference=PacePreference.FAST,
            traveling_solo=True,
            open_to_companions=True,
        ),
        ParsedTravelerIntent(
            primary_destination="TestCity",
            overall_start_date=today + timedelta(days=1),
            overall_end_date=today + timedelta(days=6),
            activities=[ActivityCategory.HIKING, ActivityCategory.SIGHTSEEING],
            budget_tier=BudgetTier.BUDGET,
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
        ),
    ]


# Tests


class TestActivityFiltering:
    """Test activity filtering logic."""

    def test_filter_removes_non_meeting_friendly(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Non-meeting-friendly activities should be filtered out."""
        recommender = ActivityRecommender(repository=mock_repository)

        candidates = mock_repository.get_activities_for_city("TestCity")
        filtered = recommender._filter_activities(
            candidates, food_lovers_profiles, food_lovers_intents
        )

        activity_ids = [a.id for a in filtered]
        assert "test-not-meeting-friendly" not in activity_ids

    def test_filter_removes_too_long_activities(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Activities longer than 8 hours should be filtered."""
        recommender = ActivityRecommender(repository=mock_repository)

        candidates = mock_repository.get_activities_for_city("TestCity")
        filtered = recommender._filter_activities(
            candidates, food_lovers_profiles, food_lovers_intents
        )

        activity_ids = [a.id for a in filtered]
        assert "test-long-activity" not in activity_ids

    def test_filter_respects_budget_constraints(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Activities above budget should be filtered."""
        recommender = ActivityRecommender(repository=mock_repository)

        candidates = mock_repository.get_activities_for_city("TestCity")
        filtered = recommender._filter_activities(
            candidates, food_lovers_profiles, food_lovers_intents
        )

        # Luxury activity should be filtered (travelers have moderate budget)
        activity_ids = [a.id for a in filtered]
        assert "test-expensive-tour" not in activity_ids

    def test_filter_allows_activities_within_budget(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Activities within budget should pass filter."""
        recommender = ActivityRecommender(repository=mock_repository)

        candidates = mock_repository.get_activities_for_city("TestCity")
        filtered = recommender._filter_activities(
            candidates, food_lovers_profiles, food_lovers_intents
        )

        activity_ids = [a.id for a in filtered]
        assert "test-food-tour" in activity_ids  # Moderate cost
        assert "test-hiking" in activity_ids  # Budget cost


class TestActivityScoring:
    """Test activity scoring logic."""

    def test_interest_match_increases_score(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Activities matching traveler interests should score higher."""
        recommender = ActivityRecommender(repository=mock_repository)

        food_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-food-tour"
        )
        hiking_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-hiking"
        )

        food_score = recommender._calculate_interest_match(
            food_activity, food_lovers_intents
        )
        hiking_score = recommender._calculate_interest_match(
            hiking_activity, food_lovers_intents
        )

        assert food_score > hiking_score

    def test_budget_compatibility_scoring(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Budget-compatible activities should score 1.0."""
        recommender = ActivityRecommender(repository=mock_repository)

        budget_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-hiking"
        )

        budget_score = recommender._calculate_budget_compatibility(
            budget_activity, food_lovers_intents
        )

        assert budget_score == 1.0  # Budget activity, moderate budget travelers

    def test_expensive_activity_lower_budget_score(
        self, mock_repository, hikers_profiles, hikers_intents
    ):
        """Expensive activities score lower for budget travelers."""
        recommender = ActivityRecommender(repository=mock_repository)

        luxury_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-expensive-tour"
        )

        budget_score = recommender._calculate_budget_compatibility(
            luxury_activity, hikers_intents
        )

        assert budget_score < 0.5  # Luxury activity, budget travelers

    def test_introvert_score_higher_for_quiet_activities(
        self, mock_repository, food_lovers_profiles
    ):
        """Quieter activities should have higher introvert scores."""
        recommender = ActivityRecommender(repository=mock_repository)

        museum = next(
            a for a in mock_repository.test_activities if a.id == "test-museum"
        )

        score = recommender._calculate_introvert_score(museum, food_lovers_profiles)

        assert score >= 0.7  # Museum has high introvert_score

    def test_activity_scoring_combines_factors(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Overall scoring should combine multiple factors."""
        recommender = ActivityRecommender(repository=mock_repository)

        candidates = [
            a
            for a in mock_repository.test_activities
            if a.meeting_friendly and a.duration_hours <= 8.0
        ]

        scored = recommender._score_activities(
            candidates, food_lovers_profiles, food_lovers_intents
        )

        # Food tour should score highest for food lovers
        food_tour_score = next(
            score for activity, score in scored if activity.id == "test-food-tour"
        )

        other_scores = [
            score
            for activity, score in scored
            if activity.id != "test-food-tour"
        ]

        assert food_tour_score > min(other_scores)


class TestRecommendationGeneration:
    """Test recommendation generation and explanations."""

    def test_recommend_returns_limited_results(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Should return at most `limit` recommendations."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        assert len(response.recommendations) <= 3

    def test_recommend_sorts_by_score(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Recommendations should be sorted by score (highest first)."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=5
        )

        scores = [rec.score for rec in response.recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_shared_interests_identified(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Should identify shared interests between travelers."""
        recommender = ActivityRecommender(repository=mock_repository)

        food_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-food-tour"
        )

        shared = recommender._find_shared_interests(food_activity, food_lovers_intents)

        assert len(shared) > 0
        assert any("food" in s.lower() for s in shared)

    def test_baseline_explanation_includes_activity_description(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Baseline explanation should include activity description."""
        recommender = ActivityRecommender(repository=mock_repository)

        food_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-food-tour"
        )

        explanation = recommender._generate_baseline_explanation(
            food_activity, ["Food Tours"], food_lovers_profiles, food_lovers_intents
        )

        assert food_activity.description in explanation

    def test_meeting_suggestion_includes_activity_name(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Meeting suggestion should mention the activity."""
        recommender = ActivityRecommender(repository=mock_repository)

        food_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-food-tour"
        )

        suggestion = recommender._generate_meeting_suggestion(
            food_activity, food_lovers_profiles, food_lovers_intents
        )

        assert food_activity.name in suggestion or "food" in suggestion.lower()

    def test_meeting_suggestion_mentions_reservation_if_needed(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Should mention if reservation is required."""
        recommender = ActivityRecommender(repository=mock_repository)

        # Create activity with reservation required
        activity_with_reservation = Activity(
            id="test-reservation",
            name="Cooking Class",
            description="Hands-on cooking",
            city="TestCity",
            tags=[ActivityTag.FOOD],
            cost_level=CostLevel.MODERATE,
            duration_hours=3.0,
            best_time=[TimeOfDay.AFTERNOON],
            best_for=["food_tours"],
            reservation_required=True,
            meeting_friendly=True,
        )

        suggestion = recommender._generate_meeting_suggestion(
            activity_with_reservation, food_lovers_profiles, food_lovers_intents
        )

        assert "book" in suggestion.lower() or "reservation" in suggestion.lower()

    def test_cost_estimate_provided(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Recommendations should include cost estimates."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        for rec in response.recommendations:
            assert rec.estimated_cost_per_person is not None

    def test_reasons_include_shared_interest(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Reasons should identify shared interests."""
        recommender = ActivityRecommender(repository=mock_repository)

        food_activity = next(
            a for a in mock_repository.test_activities if a.id == "test-food-tour"
        )

        reasons = recommender._determine_reasons(
            food_activity, food_lovers_profiles, food_lovers_intents
        )

        from wanderwing.schemas.activity import RecommendationReason

        assert RecommendationReason.SHARED_INTEREST in reasons


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_activity_list_returns_empty_recommendations(
        self, food_lovers_profiles, food_lovers_intents
    ):
        """Should handle empty activity list gracefully."""

        class EmptyRepository(ActivityRepository):
            def get_activities_for_city(self, city: str):
                return []

        recommender = ActivityRecommender(repository=EmptyRepository())

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        assert len(response.recommendations) == 0
        assert response.fallback_mode is True

    def test_requires_at_least_two_travelers(
        self, food_lovers_profiles, food_lovers_intents, mock_repository
    ):
        """Should require at least 2 travelers."""
        recommender = ActivityRecommender(repository=mock_repository)

        with pytest.raises(ValueError, match="at least 2 travelers"):
            recommender.recommend(
                food_lovers_profiles[:1], food_lovers_intents[:1], limit=3
            )

    def test_requires_matching_profile_intent_counts(
        self, food_lovers_profiles, food_lovers_intents, mock_repository
    ):
        """Profiles and intents must have same length."""
        recommender = ActivityRecommender(repository=mock_repository)

        with pytest.raises(ValueError, match="same length"):
            recommender.recommend(
                food_lovers_profiles, food_lovers_intents[:1], limit=3
            )

    def test_requires_destination(self, food_lovers_profiles, mock_repository):
        """Should require destination to be specified."""
        recommender = ActivityRecommender(repository=mock_repository)

        intents_no_destination = [
            ParsedTravelerIntent(
                primary_destination=None,
                traveling_solo=True,
                open_to_companions=True,
            ),
            ParsedTravelerIntent(
                primary_destination=None,
                traveling_solo=True,
                open_to_companions=True,
            ),
        ]

        with pytest.raises(ValueError, match="Destination must be specified"):
            recommender.recommend(
                food_lovers_profiles, intents_no_destination, limit=3
            )


class TestResponseMetadata:
    """Test response metadata and structure."""

    def test_response_includes_destination(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Response should include destination."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        assert response.destination == "TestCity"

    def test_response_includes_traveler_count(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Response should include traveler count."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        assert response.traveler_count == 2

    def test_response_includes_date_range(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Response should include overlapping date range."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        assert response.date_range is not None
        assert "Apr" in response.date_range or response.date_range  # Has dates

    def test_baseline_recommendations_not_llm_enhanced(
        self, mock_repository, food_lovers_profiles, food_lovers_intents
    ):
        """Baseline recommendations should be marked as not LLM-enhanced."""
        recommender = ActivityRecommender(repository=mock_repository)

        response = recommender.recommend(
            food_lovers_profiles, food_lovers_intents, limit=3
        )

        assert response.llm_used is False
        for rec in response.recommendations:
            assert rec.llm_enhanced is False
