"""Comprehensive unit tests for Pydantic schemas."""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from wanderwing.schemas.experiment import ExperimentAssignment, ExperimentVariant, VariantType
from wanderwing.schemas.feedback_enhanced import (
    FeedbackEvent,
    FeedbackEventType,
    MatchRatingRequest,
    ReportReason,
    ReportSeverity,
    UserReportRequest,
)
from wanderwing.schemas.match_enhanced import (
    CompatibilityDimension,
    DimensionScore,
    MatchCandidate,
    MatchExplanation,
    MatchReason,
)
from wanderwing.schemas.profile import (
    AgeRange,
    Gender,
    LanguageProficiency,
    LanguageSkill,
    SafetyPreferences,
    TravelPreferences,
    TravelStyle,
    TravelerProfileCreate,
)
from wanderwing.schemas.recommendation import (
    ActivityRecommendation,
    CostRange,
    DifficultyLevel,
    RecommendationType,
)
from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    DestinationStay,
    ParsedTravelerIntent,
    TripSegment,
    TransportMode,
)


class TestProfileSchemas:
    """Test traveler profile schemas."""

    def test_language_skill_valid(self):
        """Test valid language skill creation."""
        skill = LanguageSkill(language="Spanish", proficiency=LanguageProficiency.CONVERSATIONAL)
        assert skill.language == "Spanish"
        assert skill.proficiency == LanguageProficiency.CONVERSATIONAL

    def test_travel_preferences_valid(self):
        """Test valid travel preferences."""
        prefs = TravelPreferences(
            travel_styles=[TravelStyle.ADVENTURE, TravelStyle.CULTURE],
            budget_per_day_usd=100,
            interests=["hiking", "photography", "food"],
        )
        assert len(prefs.travel_styles) == 2
        assert prefs.budget_per_day_usd == 100
        assert "hiking" in prefs.interests

    def test_travel_preferences_min_styles(self):
        """Test travel preferences requires at least one style."""
        with pytest.raises(ValidationError) as exc_info:
            TravelPreferences(travel_styles=[])

        errors = exc_info.value.errors()
        assert any("at least 1 item" in str(err) for err in errors)

    def test_travel_preferences_max_styles(self):
        """Test travel preferences enforces max styles."""
        with pytest.raises(ValidationError):
            TravelPreferences(
                travel_styles=[
                    TravelStyle.ADVENTURE,
                    TravelStyle.CULTURE,
                    TravelStyle.FOOD,
                    TravelStyle.NATURE,
                    TravelStyle.LUXURY,
                    TravelStyle.BUDGET,  # 6 items, max is 5
                ]
            )

    def test_travel_preferences_filters_empty_interests(self):
        """Test interests validation removes empty strings."""
        prefs = TravelPreferences(
            travel_styles=[TravelStyle.ADVENTURE],
            interests=["hiking", "", "  ", "food"],
        )
        assert len(prefs.interests) == 2
        assert "" not in prefs.interests

    def test_safety_preferences_defaults(self):
        """Test safety preferences have sensible defaults."""
        prefs = SafetyPreferences()
        assert prefs.share_exact_dates is True
        assert prefs.require_verified_profiles is True
        assert prefs.share_phone_number is False

    def test_traveler_profile_create_valid(self):
        """Test valid traveler profile creation."""
        profile = TravelerProfileCreate(
            email="test@example.com",
            password="SecurePass123",
            name="Test User",
            bio="A meaningful bio with more than ten characters",
            age_range=AgeRange.TWENTY_FIVE_TO_THIRTY_FOUR,
            gender=Gender.FEMALE,
            preferences=TravelPreferences(
                travel_styles=[TravelStyle.ADVENTURE],
            ),
        )
        assert profile.email == "test@example.com"
        assert profile.name == "Test User"

    def test_traveler_profile_password_validation(self):
        """Test password strength requirements."""
        # Missing uppercase
        with pytest.raises(ValidationError) as exc_info:
            TravelerProfileCreate(
                email="test@example.com",
                password="lowercase123",
                name="Test",
                preferences=TravelPreferences(travel_styles=[TravelStyle.ADVENTURE]),
            )
        errors = exc_info.value.errors()
        assert any("uppercase" in str(err).lower() for err in errors)

        # Missing digit
        with pytest.raises(ValidationError) as exc_info:
            TravelerProfileCreate(
                email="test@example.com",
                password="NoNumbers",
                name="Test",
                preferences=TravelPreferences(travel_styles=[TravelStyle.ADVENTURE]),
            )
        errors = exc_info.value.errors()
        assert any("digit" in str(err).lower() for err in errors)

    def test_traveler_profile_bio_min_length(self):
        """Test bio must be meaningful if provided."""
        with pytest.raises(ValidationError) as exc_info:
            TravelerProfileCreate(
                email="test@example.com",
                password="SecurePass123",
                name="Test",
                bio="Short",  # Less than 10 chars
                preferences=TravelPreferences(travel_styles=[TravelStyle.ADVENTURE]),
            )
        errors = exc_info.value.errors()
        assert any("at least 10 characters" in str(err) for err in errors)

    def test_traveler_profile_social_links_validation(self):
        """Test social media links validation."""
        with pytest.raises(ValidationError) as exc_info:
            TravelerProfileCreate(
                email="test@example.com",
                password="SecurePass123",
                name="Test",
                social_media_links={"invalid_platform": "https://example.com"},
                preferences=TravelPreferences(travel_styles=[TravelStyle.ADVENTURE]),
            )
        errors = exc_info.value.errors()
        assert any("not allowed" in str(err) for err in errors)


class TestTripSchemas:
    """Test trip-related schemas."""

    def test_destination_stay_valid(self):
        """Test valid destination stay creation."""
        stay = DestinationStay(
            destination="Tokyo",
            country="Japan",
            start_date=date(2024, 4, 1),
            end_date=date(2024, 4, 6),
            nights=5,
        )
        assert stay.destination == "Tokyo"
        assert stay.nights == 5

    def test_destination_stay_date_validation(self):
        """Test destination stay validates dates."""
        with pytest.raises(ValidationError) as exc_info:
            DestinationStay(
                destination="Tokyo",
                country="Japan",
                start_date=date(2024, 4, 10),
                end_date=date(2024, 4, 1),  # End before start
                nights=5,
            )
        errors = exc_info.value.errors()
        assert any("after start_date" in str(err) for err in errors)

    def test_destination_stay_nights_calculation(self):
        """Test nights must match date range."""
        with pytest.raises(ValidationError) as exc_info:
            DestinationStay(
                destination="Tokyo",
                country="Japan",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 6),
                nights=10,  # Should be 5
            )
        errors = exc_info.value.errors()
        assert any("doesn't match date range" in str(err) for err in errors)

    def test_trip_segment_valid(self):
        """Test valid trip segment creation."""
        segment = TripSegment(
            from_destination="Tokyo",
            to_destination="Kyoto",
            departure_date=date(2024, 4, 6),
            arrival_date=date(2024, 4, 6),
            transport_mode=TransportMode.TRAIN,
        )
        assert segment.transport_mode == TransportMode.TRAIN

    def test_trip_segment_date_validation(self):
        """Test trip segment validates arrival after departure."""
        with pytest.raises(ValidationError) as exc_info:
            TripSegment(
                from_destination="Tokyo",
                to_destination="Kyoto",
                departure_date=date(2024, 4, 6),
                arrival_date=date(2024, 4, 5),  # Before departure
                transport_mode=TransportMode.TRAIN,
            )
        errors = exc_info.value.errors()
        assert any("cannot be before departure" in str(err) for err in errors)

    def test_parsed_traveler_intent_valid(self):
        """Test valid parsed traveler intent."""
        intent = ParsedTravelerIntent(
            raw_input="Going to Tokyo for a week",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 8),
                    nights=7,
                )
            ],
            activities=[ActivityCategory.SIGHTSEEING, ActivityCategory.FOOD_TOUR],
            budget_tier=BudgetTier.MODERATE,
            confidence_score=0.9,
        )
        assert intent.primary_destination == "Tokyo"
        assert len(intent.destination_stays) == 1

    def test_parsed_intent_chronological_stays(self):
        """Test destination stays must be chronological."""
        with pytest.raises(ValidationError) as exc_info:
            ParsedTravelerIntent(
                raw_input="Multi-city trip",
                primary_destination="Tokyo",
                destination_stays=[
                    DestinationStay(
                        destination="Kyoto",
                        country="Japan",
                        start_date=date(2024, 4, 10),
                        end_date=date(2024, 4, 15),
                        nights=5,
                    ),
                    DestinationStay(
                        destination="Tokyo",
                        country="Japan",
                        start_date=date(2024, 4, 1),
                        end_date=date(2024, 4, 10),
                        nights=9,
                    ),
                ],
            )
        errors = exc_info.value.errors()
        assert any("chronological order" in str(err) for err in errors)

    def test_parsed_intent_calculates_overall_dates(self):
        """Test overall dates are calculated from stays."""
        intent = ParsedTravelerIntent(
            raw_input="Multi-city trip",
            primary_destination="Tokyo",
            destination_stays=[
                DestinationStay(
                    destination="Tokyo",
                    country="Japan",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 6),
                    nights=5,
                ),
                DestinationStay(
                    destination="Kyoto",
                    country="Japan",
                    start_date=date(2024, 4, 6),
                    end_date=date(2024, 4, 10),
                    nights=4,
                ),
            ],
        )
        assert intent.overall_start_date == date(2024, 4, 1)
        assert intent.overall_end_date == date(2024, 4, 10)
        assert intent.total_duration_days == 9


class TestMatchSchemas:
    """Test matching schemas."""

    def test_dimension_score_valid(self):
        """Test valid dimension score."""
        score = DimensionScore(
            dimension=CompatibilityDimension.ACTIVITIES,
            score=0.85,
            explanation="Both enjoy hiking and food tours",
        )
        assert score.dimension == CompatibilityDimension.ACTIVITIES
        assert score.score == 0.85

    def test_dimension_score_bounds(self):
        """Test dimension score bounds validation."""
        with pytest.raises(ValidationError):
            DimensionScore(
                dimension=CompatibilityDimension.BUDGET,
                score=1.5,  # > 1.0
                explanation="Test",
            )

    def test_match_explanation_valid(self):
        """Test valid match explanation."""
        explanation = MatchExplanation(
            overall_score=0.87,
            dimension_scores=[
                DimensionScore(
                    dimension=CompatibilityDimension.DESTINATION,
                    score=1.0,
                    explanation="Same destination",
                )
            ],
            primary_reasons=[MatchReason.SAME_DESTINATION],
            llm_summary="Excellent match for travel companions",
            why_great_match=["Perfect date overlap"],
            rule_based_score=0.82,
            llm_similarity_score=0.91,
        )
        assert explanation.overall_score == 0.87
        assert len(explanation.dimension_scores) == 1

    def test_match_candidate_valid(self):
        """Test valid match candidate."""
        candidate = MatchCandidate(
            match_id=123,
            traveler_profile_id=456,
            traveler_name="Test Traveler",
            traveler_verification_level=3,
            traveler_trust_score=0.85,
            destination="Tokyo",
            trip_start_date="2024-04-01",
            trip_end_date="2024-04-10",
            trip_duration_days=10,
            overlapping_days=9,
            match_explanation=MatchExplanation(
                overall_score=0.87,
                dimension_scores=[
                    DimensionScore(
                        dimension=CompatibilityDimension.DESTINATION,
                        score=1.0,
                        explanation="Same",
                    )
                ],
                primary_reasons=[MatchReason.SAME_DESTINATION],
                llm_summary="Great match",
                why_great_match=["Same destination"],
                rule_based_score=0.82,
                llm_similarity_score=0.91,
            ),
            matched_at=datetime.utcnow(),
        )
        assert candidate.destination == "Tokyo"


class TestRecommendationSchemas:
    """Test recommendation schemas."""

    def test_activity_recommendation_valid(self):
        """Test valid activity recommendation."""
        rec = ActivityRecommendation(
            title="Sunrise Hike to Mount Takao",
            description="Start early to catch the spectacular sunrise from Mount Takao's summit.",
            recommendation_type=RecommendationType.SHARED_ACTIVITY,
            activity_category="hiking",
            location="Mount Takao, Tokyo",
            difficulty_level=DifficultyLevel.MODERATE,
            duration_hours=3.5,
            cost_range=CostRange.BUDGET,
            cost_per_person_usd=12.0,
            why_recommended=["Both love hiking", "Budget-friendly"],
        )
        assert rec.difficulty_level == DifficultyLevel.MODERATE
        assert rec.cost_per_person_usd == 12.0

    def test_activity_recommendation_min_title_length(self):
        """Test recommendation title minimum length."""
        with pytest.raises(ValidationError):
            ActivityRecommendation(
                title="Hike",  # Too short
                description="A wonderful hiking experience for travelers.",
                recommendation_type=RecommendationType.SHARED_ACTIVITY,
                activity_category="hiking",
                location="Tokyo",
                why_recommended=["Test"],
            )


class TestFeedbackSchemas:
    """Test feedback schemas."""

    def test_feedback_event_valid(self):
        """Test valid feedback event."""
        event = FeedbackEvent(
            event_type=FeedbackEventType.MATCH_RATING,
            user_id=123,
            match_id=456,
            rating=5,
            comment="Great travel companion!",
        )
        assert event.rating == 5
        assert event.event_type == FeedbackEventType.MATCH_RATING

    def test_feedback_event_comment_min_length(self):
        """Test feedback comment minimum length when provided."""
        with pytest.raises(ValidationError) as exc_info:
            FeedbackEvent(
                event_type=FeedbackEventType.MATCH_RATING,
                user_id=123,
                comment="Bad",  # Too short
            )
        errors = exc_info.value.errors()
        assert any("at least 5 characters" in str(err) for err in errors)

    def test_match_rating_request_valid(self):
        """Test valid match rating request."""
        rating = MatchRatingRequest(
            match_id=456,
            rating=5,
            comment="Excellent companion",
            would_travel_again=True,
            tags=["great_match"],
        )
        assert rating.rating == 5
        assert rating.would_travel_again is True

    def test_match_rating_bounds(self):
        """Test match rating bounds."""
        with pytest.raises(ValidationError):
            MatchRatingRequest(
                match_id=456,
                rating=6,  # > 5
            )

    def test_user_report_request_valid(self):
        """Test valid user report request."""
        report = UserReportRequest(
            reported_user_id=789,
            reason=ReportReason.SPAM,
            details="User sent multiple unsolicited promotional messages.",
            severity=ReportSeverity.LOW,
        )
        assert report.reason == ReportReason.SPAM
        assert report.severity == ReportSeverity.LOW

    def test_user_report_details_min_length(self):
        """Test user report requires detailed explanation."""
        with pytest.raises(ValidationError):
            UserReportRequest(
                reported_user_id=789,
                reason=ReportReason.SPAM,
                details="Spam",  # Too short
            )


class TestExperimentSchemas:
    """Test experiment schemas."""

    def test_experiment_assignment_valid(self):
        """Test valid experiment assignment."""
        assignment = ExperimentAssignment(
            experiment_name="test_prompt_v2",
            variant_name="treatment",
            user_id=123,
            converted=False,
        )
        assert assignment.experiment_name == "test_prompt_v2"
        assert assignment.converted is False

    def test_experiment_variant_valid(self):
        """Test valid experiment variant."""
        variant = ExperimentVariant(
            name="control",
            description="Original version",
            allocation_percentage=50.0,
            is_control=True,
        )
        assert variant.allocation_percentage == 50.0
        assert variant.is_control is True

    def test_experiment_variant_percentage_bounds(self):
        """Test variant percentage bounds."""
        with pytest.raises(ValidationError):
            ExperimentVariant(
                name="test",
                description="Test",
                allocation_percentage=150.0,  # > 100
            )


class TestSchemaExamples:
    """Test that schema examples are valid."""

    def test_profile_example_valid(self):
        """Test traveler profile example is valid."""
        example = TravelerProfileCreate.model_config["json_schema_extra"]["example"]
        profile = TravelerProfileCreate(**example)
        assert profile.email == "alice.chen@example.com"

    def test_destination_stay_example_valid(self):
        """Test destination stay example is valid."""
        example = DestinationStay.model_config["json_schema_extra"]["example"]
        stay = DestinationStay(**example)
        assert stay.destination == "Tokyo"

    def test_parsed_intent_example_valid(self):
        """Test parsed intent example is valid."""
        example = ParsedTravelerIntent.model_config["json_schema_extra"]["example"]
        intent = ParsedTravelerIntent(**example)
        assert intent.primary_destination == "Tokyo"

    def test_activity_recommendation_example_valid(self):
        """Test activity recommendation example is valid."""
        example = ActivityRecommendation.model_config["json_schema_extra"]["example"]
        rec = ActivityRecommendation(**example)
        assert rec.title == "Sunrise Hike to Mount Takao Summit"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_trimming(self):
        """Test that empty strings are properly handled."""
        prefs = TravelPreferences(
            travel_styles=[TravelStyle.ADVENTURE],
            interests=["  hiking  ", "", "   "],
        )
        # Should remove empty/whitespace-only items
        assert len(prefs.interests) == 1
        assert prefs.interests[0] == "hiking"

    def test_maximum_field_lengths(self):
        """Test maximum field length validation."""
        long_string = "x" * 2001

        with pytest.raises(ValidationError):
            FeedbackEvent(
                event_type=FeedbackEventType.MATCH_RATING,
                user_id=123,
                comment=long_string,  # > 2000
            )

    def test_enum_validation(self):
        """Test enum validation rejects invalid values."""
        with pytest.raises(ValidationError):
            TravelPreferences(
                travel_styles=["invalid_style"],  # Not a valid TravelStyle
            )

    def test_date_edge_cases(self):
        """Test date handling edge cases."""
        # Same day trip
        stay = DestinationStay(
            destination="Tokyo",
            country="Japan",
            start_date=date(2024, 4, 1),
            end_date=date(2024, 4, 2),
            nights=1,
        )
        assert stay.nights == 1

    def test_score_precision(self):
        """Test score values maintain precision."""
        score = DimensionScore(
            dimension=CompatibilityDimension.ACTIVITIES,
            score=0.123456789,
            explanation="Test",
        )
        # Should accept high precision
        assert score.score == pytest.approx(0.123456789)
