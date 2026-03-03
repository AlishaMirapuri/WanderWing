"""Activity recommendation schemas."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl


class RecommendationType(str, Enum):
    """Type of recommendation."""

    SHARED_ACTIVITY = "shared_activity"
    COST_SAVING = "cost_saving"
    SAFETY_TIP = "safety_tip"
    LOCAL_INSIGHT = "local_insight"
    ITINERARY_OPTIMIZATION = "itinerary_optimization"


class DifficultyLevel(str, Enum):
    """Activity difficulty level."""

    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    EXPERT = "expert"


class CostRange(str, Enum):
    """Cost range for activity."""

    FREE = "free"
    BUDGET = "budget"  # <$20
    MODERATE = "moderate"  # $20-50
    EXPENSIVE = "expensive"  # $50-100
    LUXURY = "luxury"  # >$100


class ActivityRecommendation(BaseModel):
    """Recommended activity for matched travelers."""

    id: int | None = None
    title: Annotated[str, Field(min_length=5, max_length=200)]
    description: Annotated[str, Field(min_length=20, max_length=2000)]
    recommendation_type: RecommendationType

    # Activity details
    activity_category: str
    location: Annotated[str, Field(min_length=2, max_length=200)]
    difficulty_level: DifficultyLevel | None = None
    duration_hours: Annotated[float | None, Field(ge=0.5, le=24)] = None
    cost_range: CostRange | None = None
    cost_per_person_usd: Annotated[float | None, Field(ge=0, le=10000)] = None

    # Group details
    ideal_group_size: Annotated[int, Field(ge=1, le=20)] = 2
    cost_savings_if_shared: Annotated[float | None, Field(ge=0)] = None

    # Scheduling
    best_time_of_day: Annotated[str | None, Field(max_length=50)] = None
    suggested_date: datetime | None = None
    advance_booking_required: bool = False
    booking_url: HttpUrl | None = None

    # Why recommended
    why_recommended: Annotated[list[str], Field(min_length=1, max_length=10)]
    matches_interests: Annotated[list[str], Field(max_length=10)] = []

    # Metadata
    confidence_score: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    source: Annotated[str, Field(max_length=100)] = "llm_generated"
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 789,
                "title": "Sunrise Hike to Mount Takao Summit",
                "description": "Start early to catch the spectacular sunrise from Mount Takao's summit. This moderate 3-hour hike offers stunning views of Tokyo and, on clear days, Mount Fuji. The trail is well-maintained with rest stations. After the hike, enjoy traditional soba noodles at the mountain base restaurants.",
                "recommendation_type": "shared_activity",
                "activity_category": "hiking",
                "location": "Mount Takao, Hachioji, Tokyo",
                "difficulty_level": "moderate",
                "duration_hours": 3.5,
                "cost_range": "budget",
                "cost_per_person_usd": 12.0,
                "ideal_group_size": 2,
                "cost_savings_if_shared": 8.0,
                "best_time_of_day": "Early morning (4:30 AM start)",
                "suggested_date": "2024-04-03T04:30:00Z",
                "advance_booking_required": False,
                "booking_url": "https://www.takao599.com/",
                "why_recommended": [
                    "Both travelers love hiking",
                    "Matches 'early bird' preference",
                    "Budget-friendly activity",
                    "Great for photography",
                    "Can share taxi cost to trailhead",
                ],
                "matches_interests": ["hiking", "photography", "nature"],
                "confidence_score": 0.94,
                "source": "llm_generated",
            }
        }
    }


class RecommendationRequest(BaseModel):
    """Request for activity recommendations."""

    match_id: int
    user_id: int
    destination: str
    start_date: datetime
    end_date: datetime
    max_recommendations: Annotated[int, Field(ge=1, le=20)] = 5
    include_cost_saving_tips: bool = True
    budget_constraint_usd: Annotated[float | None, Field(ge=0)] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "match_id": 456,
                "user_id": 123,
                "destination": "Tokyo",
                "start_date": "2024-04-01T00:00:00Z",
                "end_date": "2024-04-10T00:00:00Z",
                "max_recommendations": 5,
                "include_cost_saving_tips": True,
                "budget_constraint_usd": 500.0,
            }
        }
    }


class RecommendationResponse(BaseModel):
    """Response with activity recommendations."""

    recommendations: list[ActivityRecommendation]
    total_recommendations: int
    estimated_total_cost_usd: float
    estimated_cost_savings_usd: float
    processing_time_ms: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "recommendations": [
                    {
                        "title": "Sunrise Hike to Mount Takao Summit",
                        "description": "Start early to catch...",
                        "cost_per_person_usd": 12.0,
                    }
                ],
                "total_recommendations": 5,
                "estimated_total_cost_usd": 234.0,
                "estimated_cost_savings_usd": 78.0,
                "processing_time_ms": 1890,
            }
        }
    }
