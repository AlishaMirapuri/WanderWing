"""
Activity and recommendation schemas.

Defines structured data for activities, recommendations, and tags.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ActivityTag(str, Enum):
    """Tags for categorizing activities."""

    FOOD = "food"
    OUTDOORS = "outdoors"
    CULTURE = "culture"
    NIGHTLIFE = "nightlife"
    LOW_COST = "low-cost"
    INTROVERT_FRIENDLY = "introvert-friendly"
    ADVENTURE = "adventure"
    WELLNESS = "wellness"
    SHOPPING = "shopping"
    LOCAL_EXPERIENCE = "local-experience"
    FAMILY_FRIENDLY = "family-friendly"
    ROMANTIC = "romantic"
    EDUCATIONAL = "educational"
    SEASONAL = "seasonal"


class CostLevel(str, Enum):
    """Cost levels for activities."""

    FREE = "free"
    BUDGET = "budget"  # Under $20
    MODERATE = "moderate"  # $20-50
    EXPENSIVE = "expensive"  # $50-100
    LUXURY = "luxury"  # $100+


class TimeOfDay(str, Enum):
    """Best time of day for activity."""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    ANYTIME = "anytime"


class Activity(BaseModel):
    """
    Represents a single activity or attraction.

    Used for both storage and recommendation.
    """

    id: str = Field(description="Unique identifier (e.g., 'tokyo-meiji-shrine')")
    name: str = Field(description="Activity name")
    description: str = Field(description="Brief description")
    city: str = Field(description="City name")
    neighborhood: Optional[str] = Field(
        default=None, description="Specific neighborhood or district"
    )
    tags: list[ActivityTag] = Field(
        default_factory=list, description="Categorization tags"
    )
    cost_level: CostLevel = Field(description="Typical cost range")
    duration_hours: float = Field(description="Typical duration in hours")
    best_time: list[TimeOfDay] = Field(
        default_factory=list, description="Best times of day"
    )
    best_for: list[str] = Field(
        default_factory=list,
        description="Activity categories this suits (hiking, food_tours, museums, etc.)",
    )
    group_size_min: int = Field(default=1, description="Minimum group size")
    group_size_max: int = Field(default=20, description="Maximum group size")
    reservation_required: bool = Field(
        default=False, description="Whether reservation is needed"
    )
    introvert_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How introvert-friendly (0=very social, 1=quiet/solo-friendly)",
    )
    physical_intensity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Physical demand (0=relaxed, 1=intense)",
    )
    cultural_depth: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Cultural immersion level (0=touristy, 1=authentic)",
    )
    typical_rating: Optional[float] = Field(
        default=None, ge=0.0, le=5.0, description="Average user rating"
    )
    meeting_friendly: bool = Field(
        default=True,
        description="Whether this is good for first-time meetups (public, safe)",
    )

    class Config:
        use_enum_values = True


class RecommendationReason(str, Enum):
    """Reasons why an activity was recommended."""

    SHARED_INTEREST = "shared-interest"
    COMPLEMENTARY_INTEREST = "complementary-interest"
    BUDGET_MATCH = "budget-match"
    PACE_MATCH = "pace-match"
    DATE_OVERLAP = "date-overlap"
    POPULAR = "popular"
    INTROVERT_FRIENDLY = "introvert-friendly"
    LOW_PRESSURE = "low-pressure"
    GOOD_CONVERSATION = "good-conversation"


class ActivityRecommendation(BaseModel):
    """
    A recommended activity with explanation and metadata.

    Output format for the recommendation engine.
    """

    activity: Activity = Field(description="The recommended activity")
    score: float = Field(
        ge=0.0, le=1.0, description="Compatibility score for this activity"
    )
    reasons: list[RecommendationReason] = Field(
        description="Why this was recommended"
    )
    explanation: str = Field(
        description="Human-readable explanation of why this activity matches"
    )
    meeting_suggestion: str = Field(
        description="Safe, low-pressure meeting invitation text"
    )
    shared_interests: list[str] = Field(
        default_factory=list,
        description="Specific interests both travelers share (hiking, food, etc.)",
    )
    best_match_for: list[str] = Field(
        default_factory=list,
        description="Which travelers this best suits (by name or ID)",
    )
    estimated_cost_per_person: Optional[str] = Field(
        default=None, description="Cost estimate (e.g., '$20-30')"
    )
    llm_enhanced: bool = Field(
        default=False,
        description="Whether explanation was enhanced by LLM",
    )

    class Config:
        use_enum_values = True


class ActivityRecommendationResponse(BaseModel):
    """
    Complete response from activity recommendation engine.

    Contains multiple recommendations with metadata.
    """

    recommendations: list[ActivityRecommendation] = Field(
        description="3-5 recommended activities"
    )
    destination: str = Field(description="Destination city")
    traveler_count: int = Field(description="Number of travelers in group")
    date_range: Optional[str] = Field(
        default=None, description="Overlapping date range"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Generation timestamp"
    )
    llm_used: bool = Field(
        default=False, description="Whether LLM enhancement was used"
    )
    fallback_mode: bool = Field(
        default=False,
        description="Whether fallback (non-LLM) explanations were used",
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
