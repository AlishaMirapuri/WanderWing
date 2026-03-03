"""Match-related Pydantic schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MatchStatus(str, Enum):
    """Match status."""

    PENDING = "pending"
    SUGGESTED = "suggested"
    VIEWED = "viewed"
    DISMISSED = "dismissed"


class ConnectionStatus(str, Enum):
    """Connection request status."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    BLOCKED = "blocked"


class MatchScore(BaseModel):
    """Detailed match scoring breakdown."""

    overall_score: float = Field(..., ge=0.0, le=1.0, description="Combined match score")
    llm_similarity: float = Field(..., ge=0.0, le=1.0, description="LLM-based similarity")
    rule_based_score: float = Field(..., ge=0.0, le=1.0, description="Rule-based compatibility")
    destination_overlap: float = Field(..., ge=0.0, le=1.0)
    date_overlap: float = Field(..., ge=0.0, le=1.0)
    activity_similarity: float = Field(..., ge=0.0, le=1.0)
    budget_compatibility: float = Field(..., ge=0.0, le=1.0)


class MatchBase(BaseModel):
    """Base match schema."""

    trip_id_1: int
    trip_id_2: int
    score: MatchScore
    llm_reasoning: str | None = Field(default=None, description="LLM explanation for match")


class MatchCreate(MatchBase):
    """Schema for creating a match."""

    pass


class Match(MatchBase):
    """Full match schema."""

    id: int
    status: MatchStatus = Field(default=MatchStatus.SUGGESTED)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchWithTrips(Match):
    """Match with full trip details."""

    trip_1_destination: str
    trip_2_destination: str
    trip_1_user_name: str
    trip_2_user_name: str
    shared_activities: list[str] = Field(default_factory=list)
    suggested_activities: list[str] = Field(default_factory=list)


class ConnectionBase(BaseModel):
    """Base connection schema."""

    match_id: int
    initiator_id: int
    message: str | None = Field(default=None, max_length=500)


class ConnectionCreate(ConnectionBase):
    """Schema for creating a connection request."""

    pass


class Connection(ConnectionBase):
    """Full connection schema."""

    id: int
    status: ConnectionStatus = Field(default=ConnectionStatus.PENDING)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
