"""Feedback-related Pydantic schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FeedbackType(str, Enum):
    """Type of feedback."""

    MATCH_RATING = "match_rating"
    REPORT = "report"
    FEATURE_REQUEST = "feature_request"
    BUG = "bug"


class ReportReason(str, Enum):
    """Reasons for reporting a user or match."""

    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    FAKE_PROFILE = "fake_profile"
    HARASSMENT = "harassment"
    SAFETY_CONCERN = "safety_concern"
    OTHER = "other"


class FeedbackBase(BaseModel):
    """Base feedback schema."""

    feedback_type: FeedbackType
    rating: int | None = Field(default=None, ge=1, le=5, description="Rating 1-5")
    comment: str | None = Field(default=None, max_length=1000)
    match_id: int | None = None
    reported_user_id: int | None = None
    report_reason: ReportReason | None = None


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback."""

    pass


class Feedback(FeedbackBase):
    """Full feedback schema."""

    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchRating(BaseModel):
    """Simplified match rating schema."""

    match_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)


class UserReport(BaseModel):
    """Simplified user report schema."""

    reported_user_id: int
    reason: ReportReason
    details: str | None = Field(default=None, max_length=1000)
