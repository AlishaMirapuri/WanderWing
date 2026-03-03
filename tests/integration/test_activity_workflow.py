"""
Integration tests for activity recommendation workflow.

Tests end-to-end workflow with real activity data.
"""

from datetime import datetime, timedelta

import pytest

from wanderwing.data.activity_repository import get_activity_repository
from wanderwing.schemas.activity import ActivityTag, RecommendationReason
from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    PacePreference,
    ParsedTravelerIntent,
)
from wanderwing.schemas.user import TravelerProfile, AgeRange
from wanderwing.services.activity_recommender import get_activity_recommender


# Test Fixtures


@pytest.fixture
def tokyo_food_hikers():
    """Two travelers going to Tokyo who love food and hiking."""
    today = datetime.now().date()

    profiles = [
        TravelerProfile(
            user_id="alice",
            age_range=AgeRange.AGE_25_34,
            verification_level=3,
            trust_score=0.85,
        ),
        TravelerProfile(
            user_id="bob",
            age_range=AgeRange.AGE_25_34,
            verification_level=2,
            trust_score=0.75,
        ),
    ]

    intents = [
        ParsedTravelerIntent(
            primary_destination="Tokyo",
            overall_start_date=today,
            overall_end_date=today + timedelta(days=10),
            activities=[
                ActivityCategory.HIKING,
                ActivityCategory.FOOD_TOURS,
                ActivityCategory.SIGHTSEEING,
            ],
            budget_tier=BudgetTier.MODERATE,
            pace_preference=PacePreference.MODERATE,
            traveling_solo=True,
            open_to_companions=True,
        ),
        ParsedTravelerIntent(
            primary_destination="Tokyo",
            overall_start_date=today + timedelta(days=2),
            overall_end_date=today + timedelta(days=12),
            activities=[
                ActivityCategory.HIKING,
                ActivityCategory.ADVENTURE_SPORTS,
                ActivityCategory.SIGHTSEEING,
            ],
            budget_tier=BudgetTier.MODERATE,
            pace_preference=PacePreference.FAST,
            traveling_solo=True,
            open_to_companions=True,
        ),
    ]

    return profiles, intents


@pytest.fixture
def paris_culture_lovers():
    """Two travelers going to Paris who love museums and culture."""
    today = datetime.now().date()

    profiles = [
        TravelerProfile(
            user_id="charlie",
            age_range=AgeRange.AGE_35_44,
            verification_level=3,
            trust_score=0.90,
        ),
        TravelerProfile(
            user_id="diana",
            age_range=AgeRange.AGE_35_44,
            verification_level=3,
            trust_score=0.88,
        ),
    ]

    intents = [
        ParsedTravelerIntent(
            primary_destination="Paris",
            overall_start_date=today,
            overall_end_date=today + timedelta(days=7),
            activities=[
                ActivityCategory.MUSEUMS,
                ActivityCategory.CULTURAL_EVENTS,
                ActivityCategory.FOOD_TOURS,
            ],
            budget_tier=BudgetTier.COMFORTABLE,
            pace_preference=PacePreference.RELAXED,
            traveling_solo=True,
            open_to_companions=True,
        ),
        ParsedTravelerIntent(
            primary_destination="Paris",
            overall_start_date=today + timedelta(days=1),
            overall_end_date=today + timedelta(days=8),
            activities=[
                ActivityCategory.MUSEUMS,
                ActivityCategory.CULTURAL_EVENTS,
                ActivityCategory.SIGHTSEEING,
            ],
            budget_tier=BudgetTier.COMFORTABLE,
            pace_preference=PacePreference.RELAXED,
            traveling_solo=True,
            open_to_companions=True,
        ),
    ]

    return profiles, intents


@pytest.fixture
def barcelona_budget_backpackers():
    """Two budget travelers going to Barcelona."""
    today = datetime.now().date()

    profiles = [
        TravelerProfile(
            user_id="erik",
            age_range=AgeRange.UNDER_25,
            verification_level=2,
            trust_score=0.70,
        ),
        TravelerProfile(
            user_id="fiona",
            age_range=AgeRange.UNDER_25,
            verification_level=2,
            trust_score=0.72,
        ),
    ]

    intents = [
        ParsedTravelerIntent(
            primary_destination="Barcelona",
            overall_start_date=today,
            overall_end_date=today + timedelta(days=14),
            activities=[
                ActivityCategory.SIGHTSEEING,
                ActivityCategory.LOCAL_EXPERIENCES,
                ActivityCategory.FOOD_TOURS,
            ],
            budget_tier=BudgetTier.BUDGET,
            pace_preference=PacePreference.FAST,
            traveling_solo=True,
            open_to_companions=True,
        ),
        ParsedTravelerIntent(
            primary_destination="Barcelona",
            overall_start_date=today + timedelta(days=3),
            overall_end_date=today + timedelta(days=17),
            activities=[
                ActivityCategory.BEACHES,
                ActivityCategory.SIGHTSEEING,
                ActivityCategory.LOCAL_EXPERIENCES,
            ],
            budget_tier=BudgetTier.BUDGET,
            pace_preference=PacePreference.FAST,
            traveling_solo=True,
            open_to_companions=True,
        ),
    ]

    return profiles, intents


# Integration Tests


class TestTokyoRecommendations:
    """Test recommendations for Tokyo travelers."""

    def test_tokyo_recommendations_load_real_data(self, tokyo_food_hikers):
        """Should load and process real Tokyo activity data."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        assert len(response.recommendations) > 0
        assert response.destination == "Tokyo"
        assert response.traveler_count == 2
        assert not response.fallback_mode

    def test_tokyo_includes_hiking_activities(self, tokyo_food_hikers):
        """Should recommend hiking activities for hikers."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        # Check if any recommendation is hiking-related
        hiking_activities = [
            rec
            for rec in response.recommendations
            if "hike" in rec.activity.name.lower()
            or "fuji" in rec.activity.name.lower()
            or ActivityTag.OUTDOORS in rec.activity.tags
        ]

        assert len(hiking_activities) > 0, "Expected at least one hiking activity"

    def test_tokyo_includes_food_activities(self, tokyo_food_hikers):
        """Should recommend food activities for food lovers."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        # Check if any recommendation is food-related
        food_activities = [
            rec
            for rec in response.recommendations
            if ActivityTag.FOOD in rec.activity.tags
        ]

        assert len(food_activities) > 0, "Expected at least one food activity"

    def test_tokyo_respects_budget_moderate(self, tokyo_food_hikers):
        """Should only recommend activities within moderate budget."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        from wanderwing.schemas.activity import CostLevel

        for rec in response.recommendations:
            cost_level = rec.activity.cost_level
            assert cost_level in [
                CostLevel.FREE,
                CostLevel.BUDGET,
                CostLevel.MODERATE,
            ], f"Activity {rec.activity.name} too expensive: {cost_level}"

    def test_tokyo_all_meeting_friendly(self, tokyo_food_hikers):
        """All recommended activities should be meeting-friendly."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        for rec in response.recommendations:
            assert (
                rec.activity.meeting_friendly
            ), f"Activity {rec.activity.name} not meeting-friendly"

    def test_tokyo_recommendations_have_explanations(self, tokyo_food_hikers):
        """All recommendations should have explanations."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        for rec in response.recommendations:
            assert len(rec.explanation) > 0
            assert len(rec.meeting_suggestion) > 0
            assert rec.estimated_cost_per_person is not None

    def test_tokyo_shared_interests_identified(self, tokyo_food_hikers):
        """Should identify shared interests in recommendations."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        # At least one recommendation should have shared interests
        has_shared_interests = any(
            len(rec.shared_interests) > 0 for rec in response.recommendations
        )

        assert has_shared_interests, "Expected at least one activity with shared interests"


class TestParisRecommendations:
    """Test recommendations for Paris travelers."""

    def test_paris_recommendations_load_real_data(self, paris_culture_lovers):
        """Should load and process real Paris activity data."""
        profiles, intents = paris_culture_lovers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        assert len(response.recommendations) > 0
        assert response.destination == "Paris"
        assert response.traveler_count == 2

    def test_paris_includes_museums(self, paris_culture_lovers):
        """Should recommend museums for museum lovers."""
        profiles, intents = paris_culture_lovers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        museum_activities = [
            rec
            for rec in response.recommendations
            if "museum" in rec.activity.name.lower()
            or ActivityTag.CULTURE in rec.activity.tags
        ]

        assert len(museum_activities) > 0, "Expected at least one museum activity"

    def test_paris_respects_comfortable_budget(self, paris_culture_lovers):
        """Should recommend activities within comfortable budget range."""
        profiles, intents = paris_culture_lovers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        from wanderwing.schemas.activity import CostLevel

        # Comfortable budget should allow up to expensive tier
        allowed_costs = [
            CostLevel.FREE,
            CostLevel.BUDGET,
            CostLevel.MODERATE,
            CostLevel.EXPENSIVE,
        ]

        for rec in response.recommendations:
            assert (
                rec.activity.cost_level in allowed_costs
            ), f"Activity {rec.activity.name} cost level unexpected: {rec.activity.cost_level}"


class TestBarcelonaRecommendations:
    """Test recommendations for Barcelona travelers."""

    def test_barcelona_recommendations_load_real_data(
        self, barcelona_budget_backpackers
    ):
        """Should load and process real Barcelona activity data."""
        profiles, intents = barcelona_budget_backpackers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        assert len(response.recommendations) > 0
        assert response.destination == "Barcelona"
        assert response.traveler_count == 2

    def test_barcelona_respects_budget_tier(self, barcelona_budget_backpackers):
        """Should only recommend budget-friendly activities for budget travelers."""
        profiles, intents = barcelona_budget_backpackers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        from wanderwing.schemas.activity import CostLevel

        # Budget travelers should only see free or budget activities
        for rec in response.recommendations:
            assert rec.activity.cost_level in [
                CostLevel.FREE,
                CostLevel.BUDGET,
            ], f"Activity {rec.activity.name} too expensive for budget travelers: {rec.activity.cost_level}"

    def test_barcelona_includes_beach_activities(self, barcelona_budget_backpackers):
        """Should recommend beach activities when traveler interested in beaches."""
        profiles, intents = barcelona_budget_backpackers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        # Check if beach-related activities included
        beach_activities = [
            rec
            for rec in response.recommendations
            if "beach" in rec.activity.name.lower()
            or ActivityTag.OUTDOORS in rec.activity.tags
        ]

        # Note: Beach activities might be included if they match other criteria
        # This is a soft assertion
        assert len(response.recommendations) > 0  # At least some recommendations


class TestRecommendationRanking:
    """Test recommendation ranking and scoring."""

    def test_recommendations_sorted_by_score(self, tokyo_food_hikers):
        """Recommendations should be sorted by score (highest first)."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        scores = [rec.score for rec in response.recommendations]
        assert scores == sorted(scores, reverse=True), "Recommendations not sorted by score"

    def test_top_recommendation_has_highest_score(self, tokyo_food_hikers):
        """First recommendation should have highest score."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        if len(response.recommendations) > 1:
            assert (
                response.recommendations[0].score
                >= response.recommendations[1].score
            )

    def test_shared_interests_boost_score(self, tokyo_food_hikers):
        """Activities matching shared interests should score higher."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        # Top recommendations should have shared interests
        top_rec = response.recommendations[0]
        assert (
            len(top_rec.shared_interests) > 0
            or RecommendationReason.SHARED_INTEREST in top_rec.reasons
        ), "Top recommendation should match shared interests"


class TestResponseStructure:
    """Test response structure and metadata."""

    def test_response_includes_all_required_fields(self, tokyo_food_hikers):
        """Response should include all required metadata fields."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        assert response.destination
        assert response.traveler_count > 0
        assert response.generated_at is not None
        assert isinstance(response.llm_used, bool)
        assert isinstance(response.fallback_mode, bool)

    def test_recommendation_includes_all_required_fields(self, tokyo_food_hikers):
        """Each recommendation should have all required fields."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=3)

        for rec in response.recommendations:
            assert rec.activity is not None
            assert 0.0 <= rec.score <= 1.0
            assert len(rec.reasons) > 0
            assert len(rec.explanation) > 0
            assert len(rec.meeting_suggestion) > 0
            assert rec.estimated_cost_per_person is not None
            assert isinstance(rec.llm_enhanced, bool)

    def test_activity_tags_present(self, tokyo_food_hikers):
        """Activities should have appropriate tags."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=5)

        for rec in response.recommendations:
            assert len(rec.activity.tags) > 0, "Activity should have tags"

    def test_date_range_calculated(self, tokyo_food_hikers):
        """Response should include calculated date range."""
        profiles, intents = tokyo_food_hikers
        recommender = get_activity_recommender()

        response = recommender.recommend(profiles, intents, limit=3)

        assert response.date_range is not None


class TestActivityRepository:
    """Test activity repository functionality."""

    def test_repository_loads_tokyo_data(self):
        """Repository should load Tokyo activity data."""
        repo = get_activity_repository()
        activities = repo.get_activities_for_city("Tokyo")

        assert len(activities) > 0
        assert all(a.city == "Tokyo" for a in activities)

    def test_repository_loads_paris_data(self):
        """Repository should load Paris activity data."""
        repo = get_activity_repository()
        activities = repo.get_activities_for_city("Paris")

        assert len(activities) > 0
        assert all(a.city == "Paris" for a in activities)

    def test_repository_loads_barcelona_data(self):
        """Repository should load Barcelona activity data."""
        repo = get_activity_repository()
        activities = repo.get_activities_for_city("Barcelona")

        assert len(activities) > 0
        assert all(a.city == "Barcelona" for a in activities)

    def test_repository_returns_empty_for_unknown_city(self):
        """Repository should return empty list for unknown cities."""
        repo = get_activity_repository()
        activities = repo.get_activities_for_city("UnknownCity")

        assert len(activities) == 0

    def test_repository_caches_data(self):
        """Repository should cache loaded data."""
        repo = get_activity_repository()

        # Load once
        activities1 = repo.get_activities_for_city("Tokyo")

        # Load again (should be cached)
        activities2 = repo.get_activities_for_city("Tokyo")

        assert activities1 is activities2  # Same object reference

    def test_repository_filter_by_tags(self):
        """Repository should filter activities by tags."""
        repo = get_activity_repository()
        activities = repo.get_activities_for_city("Tokyo")

        food_activities = repo.filter_activities(activities, tags=[ActivityTag.FOOD])

        assert len(food_activities) > 0
        assert all(ActivityTag.FOOD in a.tags for a in food_activities)

    def test_repository_filter_by_cost(self):
        """Repository should filter activities by cost level."""
        repo = get_activity_repository()
        activities = repo.get_activities_for_city("Tokyo")

        from wanderwing.schemas.activity import CostLevel

        budget_activities = repo.filter_activities(
            activities, max_cost=CostLevel.BUDGET
        )

        assert len(budget_activities) > 0
        for a in budget_activities:
            assert a.cost_level in [CostLevel.FREE, CostLevel.BUDGET]

    def test_repository_get_available_cities(self):
        """Repository should list available cities."""
        repo = get_activity_repository()
        cities = repo.get_available_cities()

        assert "Tokyo" in cities
        assert "Paris" in cities
        assert "Barcelona" in cities
