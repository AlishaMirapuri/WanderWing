"""Enhanced trip schemas with segments and destination stays."""

from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator


class TransportMode(str, Enum):
    """Transportation modes."""

    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    FERRY = "ferry"
    WALKING = "walking"
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    OTHER = "other"


class ActivityCategory(str, Enum):
    """Activity categories."""

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
    WATER_SPORTS = "water_sports"
    CULTURAL_EVENTS = "cultural_events"
    VOLUNTEERING = "volunteering"
    YOGA_WELLNESS = "yoga_wellness"
    CYCLING = "cycling"
    SKIING_SNOWBOARDING = "skiing_snowboarding"


class BudgetTier(str, Enum):
    """Budget tier classification."""

    SHOESTRING = "shoestring"  # <$30/day
    BUDGET = "budget"  # $30-75/day
    MODERATE = "moderate"  # $75-150/day
    COMFORTABLE = "comfortable"  # $150-300/day
    LUXURY = "luxury"  # >$300/day


class TripStatus(str, Enum):
    """Trip lifecycle status."""

    DRAFT = "draft"
    PLANNING = "planning"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PacePreference(str, Enum):
    """Trip pacing preference."""

    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"
    FLEXIBLE = "flexible"


class DestinationStay(BaseModel):
    """Details about a stay in a specific destination."""

    destination: Annotated[str, Field(min_length=2, max_length=100)]
    country: Annotated[str, Field(min_length=2, max_length=100)]
    start_date: date
    end_date: date
    nights: Annotated[int, Field(ge=1, le=365)]
    accommodation_type: str | None = None
    accommodation_name: str | None = None
    neighborhood: Annotated[str | None, Field(max_length=100)] = None
    activities: Annotated[list[ActivityCategory], Field(max_length=20)] = []
    must_see_attractions: Annotated[list[str], Field(max_length=10)] = []
    notes: Annotated[str | None, Field(max_length=500)] = None
    is_flexible: bool = False
    flexibility_days: Annotated[int, Field(ge=0, le=14)] = 0

    @model_validator(mode="after")
    def validate_dates(self) -> "DestinationStay":
        """Validate date consistency."""
        if self.start_date >= self.end_date:
            raise ValueError("end_date must be after start_date")

        calculated_nights = (self.end_date - self.start_date).days
        if self.nights != calculated_nights:
            raise ValueError(
                f"nights ({self.nights}) doesn't match date range ({calculated_nights} nights)"
            )

        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "destination": "Tokyo",
                "country": "Japan",
                "start_date": "2024-04-01",
                "end_date": "2024-04-06",
                "nights": 5,
                "accommodation_type": "hostel",
                "accommodation_name": "Sakura Hostel Asakusa",
                "neighborhood": "Asakusa",
                "activities": ["sightseeing", "food_tour", "museums"],
                "must_see_attractions": ["Senso-ji Temple", "Tsukiji Market", "Tokyo Skytree"],
                "notes": "Want to experience traditional Tokyo neighborhoods",
                "is_flexible": True,
                "flexibility_days": 2,
            }
        }
    }


class TripSegment(BaseModel):
    """Travel segment between destinations."""

    from_destination: Annotated[str, Field(min_length=2, max_length=100)]
    to_destination: Annotated[str, Field(min_length=2, max_length=100)]
    departure_date: date
    arrival_date: date
    transport_mode: TransportMode
    booking_reference: Annotated[str | None, Field(max_length=50)] = None
    carrier: Annotated[str | None, Field(max_length=100)] = None
    cost_usd: Annotated[float | None, Field(ge=0, le=50000)] = None
    notes: Annotated[str | None, Field(max_length=500)] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TripSegment":
        """Validate arrival is after departure."""
        if self.arrival_date < self.departure_date:
            raise ValueError("arrival_date cannot be before departure_date")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "from_destination": "Tokyo",
                "to_destination": "Kyoto",
                "departure_date": "2024-04-06",
                "arrival_date": "2024-04-06",
                "transport_mode": "train",
                "carrier": "JR Shinkansen",
                "cost_usd": 130.0,
                "notes": "Reserved seat on Nozomi train",
            }
        }
    }


class ParsedTravelerIntent(BaseModel):
    """
    Structured traveler intent extracted from natural language.

    This is the core output of the LLM intent parsing agent.
    """

    # Core trip details
    primary_destination: Annotated[str, Field(min_length=2, max_length=100)]
    destination_stays: Annotated[list[DestinationStay], Field(min_length=1, max_length=20)]
    trip_segments: Annotated[list[TripSegment], Field(max_length=20)] = []

    # Dates and duration
    overall_start_date: date | None = None
    overall_end_date: date | None = None
    total_duration_days: Annotated[int | None, Field(ge=1, le=730)] = None
    is_date_flexible: bool = False
    flexibility_window_days: Annotated[int, Field(ge=0, le=90)] = 0

    # Travel style and preferences
    activities: Annotated[list[ActivityCategory], Field(max_length=20)] = []
    budget_tier: BudgetTier = BudgetTier.MODERATE
    budget_total_usd: Annotated[float | None, Field(ge=0, le=1000000)] = None
    pace_preference: PacePreference = PacePreference.MODERATE

    # Group preferences
    traveling_solo: bool = True
    open_to_companions: bool = True
    preferred_group_size: Annotated[int, Field(ge=1, le=20)] = 2
    companion_requirements: Annotated[list[str], Field(max_length=10)] = []

    # Extraction metadata
    confidence_score: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    ambiguities: Annotated[list[str], Field(max_length=20)] = []
    clarification_questions: Annotated[list[str], Field(max_length=10)] = []
    raw_input: Annotated[str, Field(min_length=10, max_length=5000)]
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("destination_stays")
    @classmethod
    def validate_stays(cls, v: list[DestinationStay]) -> list[DestinationStay]:
        """Validate stays are in chronological order."""
        if len(v) < 2:
            return v

        for i in range(len(v) - 1):
            if v[i].end_date > v[i + 1].start_date:
                raise ValueError("Destination stays must be in chronological order without overlaps")

        return v

    @model_validator(mode="after")
    def calculate_overall_dates(self) -> "ParsedTravelerIntent":
        """Calculate overall trip dates from stays."""
        if self.destination_stays:
            self.overall_start_date = min(stay.start_date for stay in self.destination_stays)
            self.overall_end_date = max(stay.end_date for stay in self.destination_stays)
            self.total_duration_days = (self.overall_end_date - self.overall_start_date).days

        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "raw_input": "Planning a 2-week trip to Japan in April. Want to spend 5 days in Tokyo, then take the bullet train to Kyoto for 4 days, and finish with 3 days in Osaka. Love hiking, food tours, and visiting temples. Budget around $150/day.",
                "primary_destination": "Tokyo",
                "destination_stays": [
                    {
                        "destination": "Tokyo",
                        "country": "Japan",
                        "start_date": "2024-04-01",
                        "end_date": "2024-04-06",
                        "nights": 5,
                        "activities": ["hiking", "food_tour", "sightseeing"],
                        "must_see_attractions": ["Mt. Fuji", "Senso-ji Temple"],
                        "is_flexible": True,
                        "flexibility_days": 2,
                    },
                    {
                        "destination": "Kyoto",
                        "country": "Japan",
                        "start_date": "2024-04-06",
                        "end_date": "2024-04-10",
                        "nights": 4,
                        "activities": ["sightseeing", "cultural_events"],
                        "must_see_attractions": ["Fushimi Inari", "Kinkaku-ji"],
                        "is_flexible": False,
                    },
                ],
                "trip_segments": [
                    {
                        "from_destination": "Tokyo",
                        "to_destination": "Kyoto",
                        "departure_date": "2024-04-06",
                        "arrival_date": "2024-04-06",
                        "transport_mode": "train",
                        "carrier": "JR Shinkansen",
                    }
                ],
                "activities": ["hiking", "food_tour", "sightseeing", "cultural_events"],
                "budget_tier": "moderate",
                "budget_total_usd": 2100.0,
                "pace_preference": "moderate",
                "traveling_solo": True,
                "open_to_companions": True,
                "preferred_group_size": 2,
                "confidence_score": 0.92,
                "ambiguities": [],
                "clarification_questions": [],
            }
        }
    }


class TripIntentRequest(BaseModel):
    """Request to parse traveler intent from natural language."""

    raw_input: Annotated[str, Field(min_length=10, max_length=5000)]
    user_id: int | None = None
    prompt_version: Annotated[str, Field(pattern="^v\\d+$")] = "v1"

    model_config = {
        "json_schema_extra": {
            "example": {
                "raw_input": "I'm planning a 10-day solo trip to Japan in April. Want to visit Tokyo and Kyoto, try local food, and see some temples. Budget traveler.",
                "user_id": 123,
                "prompt_version": "v1",
            }
        }
    }


class TripIntentResponse(BaseModel):
    """Response from intent parsing."""

    parsed_intent: ParsedTravelerIntent
    needs_clarification: bool
    suggested_edits: Annotated[list[str], Field(max_length=10)] = []
    processing_time_ms: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "parsed_intent": {
                    "primary_destination": "Tokyo",
                    "raw_input": "Planning a trip to Japan...",
                    "confidence_score": 0.85,
                },
                "needs_clarification": True,
                "suggested_edits": [
                    "Specify exact travel dates or approximate month",
                    "Add accommodation preferences",
                ],
                "processing_time_ms": 1250,
            }
        }
    }
