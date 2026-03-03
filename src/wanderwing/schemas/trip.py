"""Trip-related Pydantic schemas."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class TripStatus(str, Enum):
    """Trip status."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityType(str, Enum):
    """Types of activities."""

    HIKING = "hiking"
    SIGHTSEEING = "sightseeing"
    FOOD_TOUR = "food_tour"
    NIGHTLIFE = "nightlife"
    BEACH = "beach"
    MUSEUMS = "museums"
    SHOPPING = "shopping"
    ADVENTURE_SPORTS = "adventure_sports"
    RELAXATION = "relaxation"
    PHOTOGRAPHY = "photography"
    LOCAL_EXPERIENCES = "local_experiences"
    NATURE = "nature"


class ParsedItinerary(BaseModel):
    """Structured itinerary data extracted by LLM."""

    destination: str = Field(..., description="Primary destination city/country")
    secondary_destinations: list[str] = Field(
        default_factory=list, description="Additional locations"
    )
    start_date: date | None = Field(default=None, description="Trip start date")
    end_date: date | None = Field(default=None, description="Trip end date")
    duration_days: int | None = Field(default=None, description="Trip duration in days")
    activities: list[ActivityType] = Field(
        default_factory=list, description="Desired activities"
    )
    budget_tier: str = Field(default="moderate", description="Budget level")
    travel_style: list[str] = Field(
        default_factory=list, description="Travel style preferences"
    )
    flexibility_days: int = Field(
        default=0, description="Date flexibility in days (+/- from start/end)"
    )
    accommodation_type: str | None = Field(default=None, description="Preferred lodging type")
    group_size_preference: str = Field(
        default="solo", description="Preferred group size (solo, small, any)"
    )
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="LLM confidence in extraction"
    )
    ambiguities: list[str] = Field(
        default_factory=list, description="Items needing clarification"
    )


class TripCreate(BaseModel):
    """Schema for creating a trip."""

    raw_input: str = Field(..., min_length=10, description="Natural language trip description")
    parsed_data: ParsedItinerary | None = None


class TripUpdate(BaseModel):
    """Schema for updating a trip."""

    parsed_data: ParsedItinerary | None = None
    status: TripStatus | None = None


class Trip(BaseModel):
    """Full trip schema."""

    id: int
    user_id: int
    raw_input: str
    parsed_data: ParsedItinerary | None = None
    status: TripStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TripWithUser(Trip):
    """Trip with user information."""

    user_name: str
    user_bio: str | None = None
