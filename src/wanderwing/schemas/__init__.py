"""Pydantic schemas for request/response validation."""

from .feedback import (
    Feedback,
    FeedbackCreate,
    FeedbackType,
    MatchRating,
    ReportReason,
    UserReport,
)
from .match import (
    Connection,
    ConnectionCreate,
    ConnectionStatus,
    Match,
    MatchCreate,
    MatchScore,
    MatchStatus,
    MatchWithTrips,
)
from .trip import (
    ActivityType,
    ParsedItinerary,
    Trip,
    TripCreate,
    TripStatus,
    TripUpdate,
    TripWithUser,
)
from .user import (
    BudgetTier,
    SafetyPreferences,
    TravelStyle,
    User,
    UserCreate,
    UserUpdate,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "TravelStyle",
    "BudgetTier",
    "SafetyPreferences",
    # Trip
    "Trip",
    "TripCreate",
    "TripUpdate",
    "TripWithUser",
    "TripStatus",
    "ActivityType",
    "ParsedItinerary",
    # Match
    "Match",
    "MatchCreate",
    "MatchWithTrips",
    "MatchStatus",
    "MatchScore",
    "Connection",
    "ConnectionCreate",
    "ConnectionStatus",
    # Feedback
    "Feedback",
    "FeedbackCreate",
    "FeedbackType",
    "ReportReason",
    "MatchRating",
    "UserReport",
]
