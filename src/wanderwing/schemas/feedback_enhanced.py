"""Enhanced feedback and event tracking schemas."""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator


class FeedbackEventType(str, Enum):
    """Types of feedback events."""

    MATCH_RATING = "match_rating"
    MATCH_VIEWED = "match_viewed"
    MATCH_INTERESTED = "match_interested"
    MATCH_DECLINED = "match_declined"
    CONNECTION_REQUESTED = "connection_requested"
    CONNECTION_ACCEPTED = "connection_accepted"
    CONNECTION_DECLINED = "connection_declined"
    TRIP_COMPLETED = "trip_completed"
    USER_REPORT = "user_report"
    USER_BLOCK = "user_block"
    RECOMMENDATION_VIEWED = "recommendation_viewed"
    RECOMMENDATION_ACCEPTED = "recommendation_accepted"
    FEATURE_FEEDBACK = "feature_feedback"
    BUG_REPORT = "bug_report"


class ReportReason(str, Enum):
    """Reasons for reporting a user."""

    SPAM = "spam"
    FAKE_PROFILE = "fake_profile"
    INAPPROPRIATE_BEHAVIOR = "inappropriate_behavior"
    HARASSMENT = "harassment"
    SAFETY_CONCERN = "safety_concern"
    SCAM_ATTEMPT = "scam_attempt"
    IMPERSONATION = "impersonation"
    OTHER = "other"


class ReportSeverity(str, Enum):
    """Severity level of a report."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackSentiment(str, Enum):
    """Sentiment of feedback."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class FeedbackEvent(BaseModel):
    """
    Comprehensive feedback event for analytics and improvement.

    This captures all user interactions for analysis and experimentation.
    """

    id: int | None = None
    event_type: FeedbackEventType
    user_id: int

    # Event context
    match_id: int | None = None
    trip_id: int | None = None
    recommendation_id: int | None = None
    target_user_id: int | None = None

    # Rating and sentiment
    rating: Annotated[int | None, Field(ge=1, le=5)] = None
    sentiment: FeedbackSentiment | None = None

    # Textual feedback
    comment: Annotated[str | None, Field(max_length=2000)] = None
    tags: Annotated[list[str], Field(max_length=20)] = []

    # For reports
    report_reason: ReportReason | None = None
    report_severity: ReportSeverity | None = None
    report_details: Annotated[str | None, Field(max_length=2000)] = None

    # Structured data
    metadata: dict[str, Any] = {}

    # Timing
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Annotated[str | None, Field(max_length=100)] = None

    # Processing status
    is_processed: bool = False
    requires_moderation: bool = False
    moderator_notes: Annotated[str | None, Field(max_length=1000)] = None

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str | None) -> str | None:
        """Clean and validate comment."""
        if v:
            v = v.strip()
            if len(v) < 5:
                raise ValueError("Comment must be at least 5 characters if provided")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata_size(cls, v: dict) -> dict:
        """Ensure metadata isn't too large."""
        import json
        if len(json.dumps(v)) > 10000:
            raise ValueError("Metadata too large (max 10KB)")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1001,
                    "event_type": "match_rating",
                    "user_id": 123,
                    "match_id": 456,
                    "rating": 5,
                    "sentiment": "very_positive",
                    "comment": "Amazing travel companion! We had such a great time hiking Mount Takao together. Bob's local knowledge was invaluable.",
                    "tags": ["great_match", "would_travel_again", "helpful"],
                    "metadata": {
                        "match_score": 0.87,
                        "days_traveled_together": 9,
                        "activities_completed": 12,
                    },
                },
                {
                    "id": 1002,
                    "event_type": "user_report",
                    "user_id": 123,
                    "target_user_id": 789,
                    "report_reason": "spam",
                    "report_severity": "low",
                    "report_details": "User sent multiple unsolicited messages promoting their tour company.",
                    "requires_moderation": True,
                },
            ]
        }
    }


class MatchRatingRequest(BaseModel):
    """Request to rate a match."""

    match_id: int
    rating: Annotated[int, Field(ge=1, le=5)]
    comment: Annotated[str | None, Field(max_length=2000)] = None
    would_travel_again: bool | None = None
    recommend_to_others: bool | None = None
    tags: Annotated[list[str], Field(max_length=10)] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "match_id": 456,
                "rating": 5,
                "comment": "Excellent travel companion. Shared great local food spots!",
                "would_travel_again": True,
                "recommend_to_others": True,
                "tags": ["great_match", "foodie", "helpful"],
            }
        }
    }


class UserReportRequest(BaseModel):
    """Request to report a user."""

    reported_user_id: int
    reason: ReportReason
    details: Annotated[str, Field(min_length=20, max_length=2000)]
    severity: ReportSeverity = ReportSeverity.MEDIUM
    evidence_urls: Annotated[list[str], Field(max_length=5)] = []
    occurred_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "reported_user_id": 789,
                "reason": "inappropriate_behavior",
                "details": "User made inappropriate comments during our hiking trip that made me uncomfortable. Specifically mentioned...",
                "severity": "high",
                "evidence_urls": ["https://example.com/screenshot1.png"],
                "occurred_at": "2024-04-05T14:30:00Z",
            }
        }
    }


class FeedbackSubmissionResponse(BaseModel):
    """Response after submitting feedback."""

    event_id: int
    status: str
    message: str
    requires_action: bool = False
    next_steps: Annotated[list[str], Field(max_length=5)] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": 1001,
                "status": "received",
                "message": "Thank you for your feedback! It helps us improve matches for everyone.",
                "requires_action": False,
                "next_steps": [],
            }
        }
    }
