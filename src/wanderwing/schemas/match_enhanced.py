"""Enhanced matching schemas with detailed explanations."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class MatchStatus(str, Enum):
    """Status of a match."""

    PENDING = "pending"
    SUGGESTED = "suggested"
    VIEWED = "viewed"
    INTERESTED = "interested"
    MUTUAL_INTEREST = "mutual_interest"
    DECLINED = "declined"
    EXPIRED = "expired"


class CompatibilityDimension(str, Enum):
    """Dimensions of compatibility scoring."""

    DESTINATION = "destination"
    DATES = "dates"
    ACTIVITIES = "activities"
    BUDGET = "budget"
    TRAVEL_STYLE = "travel_style"
    PACE = "pace"
    SOCIAL_COMPATIBILITY = "social_compatibility"
    AGE_COMPATIBILITY = "age_compatibility"
    LANGUAGE = "language"


class MatchReason(str, Enum):
    """Reasons for matching."""

    SAME_DESTINATION = "same_destination"
    OVERLAPPING_DATES = "overlapping_dates"
    SHARED_ACTIVITIES = "shared_activities"
    COMPATIBLE_BUDGET = "compatible_budget"
    SIMILAR_STYLE = "similar_style"
    COMPLEMENTARY_SKILLS = "complementary_skills"
    LANGUAGE_MATCH = "language_match"
    SIMILAR_EXPERIENCE = "similar_experience"


class DimensionScore(BaseModel):
    """Score for a specific compatibility dimension."""

    dimension: CompatibilityDimension
    score: Annotated[float, Field(ge=0.0, le=1.0)]
    weight: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    explanation: Annotated[str, Field(min_length=10, max_length=500)]
    contributing_factors: Annotated[list[str], Field(max_length=10)] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "dimension": "activities",
                "score": 0.85,
                "weight": 1.0,
                "explanation": "Both travelers are interested in hiking, food tours, and cultural experiences. 5 out of 6 activities match.",
                "contributing_factors": [
                    "hiking",
                    "food_tour",
                    "sightseeing",
                    "museums",
                    "local_experiences",
                ],
            }
        }
    }


class MatchExplanation(BaseModel):
    """Detailed explanation of why two travelers are matched."""

    overall_score: Annotated[float, Field(ge=0.0, le=1.0)]
    dimension_scores: Annotated[list[DimensionScore], Field(min_length=1, max_length=15)]
    primary_reasons: Annotated[list[MatchReason], Field(min_length=1, max_length=10)]
    shared_interests: Annotated[list[str], Field(max_length=20)] = []
    complementary_traits: Annotated[list[str], Field(max_length=10)] = []
    potential_concerns: Annotated[list[str], Field(max_length=5)] = []

    # LLM-generated insights
    llm_summary: Annotated[str, Field(min_length=50, max_length=1000)]
    why_great_match: Annotated[list[str], Field(min_length=1, max_length=5)]
    conversation_starters: Annotated[list[str], Field(max_length=5)] = []

    # Algorithmic details
    rule_based_score: Annotated[float, Field(ge=0.0, le=1.0)]
    llm_similarity_score: Annotated[float, Field(ge=0.0, le=1.0)]
    hybrid_weight_llm: Annotated[float, Field(ge=0.0, le=1.0)] = 0.6
    hybrid_weight_rules: Annotated[float, Field(ge=0.0, le=1.0)] = 0.4

    @field_validator("overall_score")
    @classmethod
    def validate_score_calculation(cls, v: float, info) -> float:
        """Ensure overall score matches hybrid calculation."""
        # This would ideally verify the calculation matches
        return round(v, 3)

    model_config = {
        "json_schema_extra": {
            "example": {
                "overall_score": 0.87,
                "dimension_scores": [
                    {
                        "dimension": "destination",
                        "score": 1.0,
                        "explanation": "Both traveling to Tokyo during the same period",
                    },
                    {
                        "dimension": "activities",
                        "score": 0.85,
                        "explanation": "5 out of 6 activities match",
                    },
                ],
                "primary_reasons": [
                    "same_destination",
                    "overlapping_dates",
                    "shared_activities",
                ],
                "shared_interests": ["hiking", "food tours", "photography", "temples"],
                "complementary_traits": [
                    "One has local language skills",
                    "Different accommodation preferences allow cost sharing",
                ],
                "potential_concerns": ["Slightly different pace preferences"],
                "llm_summary": "Alice and Bob are an excellent match for travel companions. Both are visiting Tokyo in early April with a strong interest in outdoor activities and authentic cultural experiences. Alice's photography skills complement Bob's interest in finding photogenic locations, while Bob's Japanese language ability will be invaluable for navigating local restaurants.",
                "why_great_match": [
                    "Perfect date overlap (April 1-10)",
                    "Shared passion for hiking and food",
                    "Complementary skills (photography + language)",
                    "Similar budget range ($100-120/day)",
                    "Both prefer small group sizes",
                ],
                "conversation_starters": [
                    "What's your dream hike around Tokyo?",
                    "Have you planned any specific food tours?",
                    "Want to split a guide for Mt. Fuji?",
                ],
                "rule_based_score": 0.82,
                "llm_similarity_score": 0.91,
                "hybrid_weight_llm": 0.6,
                "hybrid_weight_rules": 0.4,
            }
        }
    }


class MatchCandidate(BaseModel):
    """A potential travel companion match."""

    match_id: int
    traveler_profile_id: int
    traveler_name: str
    traveler_avatar_url: str | None = None
    traveler_verification_level: Annotated[int, Field(ge=0, le=5)]
    traveler_trust_score: Annotated[float, Field(ge=0.0, le=1.0)]

    # Trip details
    destination: str
    trip_start_date: str  # ISO format
    trip_end_date: str  # ISO format
    trip_duration_days: int
    overlapping_days: int

    # Match quality
    match_explanation: MatchExplanation
    match_status: MatchStatus = MatchStatus.SUGGESTED

    # Timing
    matched_at: datetime
    expires_at: datetime | None = None
    viewed_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "match_id": 456,
                "traveler_profile_id": 789,
                "traveler_name": "Bob Martinez",
                "traveler_avatar_url": "https://example.com/avatars/bob.jpg",
                "traveler_verification_level": 3,
                "traveler_trust_score": 0.89,
                "destination": "Tokyo",
                "trip_start_date": "2024-04-01",
                "trip_end_date": "2024-04-10",
                "trip_duration_days": 10,
                "overlapping_days": 9,
                "match_explanation": {
                    "overall_score": 0.87,
                    "primary_reasons": ["same_destination", "overlapping_dates"],
                    "llm_summary": "Excellent match...",
                    "why_great_match": ["Perfect date overlap"],
                    "rule_based_score": 0.82,
                    "llm_similarity_score": 0.91,
                },
                "match_status": "suggested",
                "matched_at": "2024-03-15T10:30:00Z",
            }
        }
    }


class MatchRequest(BaseModel):
    """Request to find matches for a trip."""

    trip_id: int
    user_id: int
    min_score: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    max_results: Annotated[int, Field(ge=1, le=50)] = 10
    require_date_overlap: bool = True
    min_overlap_days: Annotated[int, Field(ge=0, le=365)] = 1
    filters: dict[str, str | int | float | bool] = {}

    model_config = {
        "json_schema_extra": {
            "example": {
                "trip_id": 123,
                "user_id": 456,
                "min_score": 0.6,
                "max_results": 10,
                "require_date_overlap": True,
                "min_overlap_days": 3,
                "filters": {"min_verification_level": 2, "same_gender_only": False},
            }
        }
    }


class MatchResponse(BaseModel):
    """Response with match candidates."""

    candidates: list[MatchCandidate]
    total_candidates: int
    search_criteria: MatchRequest
    processing_time_ms: int
    cache_hit: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "candidates": [
                    {
                        "match_id": 456,
                        "traveler_name": "Bob Martinez",
                        "destination": "Tokyo",
                        "match_explanation": {"overall_score": 0.87},
                    }
                ],
                "total_candidates": 1,
                "search_criteria": {"trip_id": 123, "min_score": 0.6},
                "processing_time_ms": 2340,
                "cache_hit": False,
            }
        }
    }
