"""SQLAlchemy database models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from wanderwing.schemas.feedback import FeedbackType, ReportReason
from wanderwing.schemas.match import ConnectionStatus, MatchStatus
from wanderwing.schemas.trip import TripStatus
from wanderwing.schemas.user import BudgetTier

from .base import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Mapped


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Travel preferences stored as JSON
    travel_styles: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    budget_tier: Mapped[str] = mapped_column(
        Enum(BudgetTier), default=BudgetTier.MODERATE, nullable=False
    )
    safety_preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Status flags
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="user")
    feedback_given: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user")


class Trip(Base):
    """Trip model."""

    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Trip data
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(
        Enum(TripStatus), default=TripStatus.ACTIVE, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="trips")


class Match(Base):
    """Match model."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id_1: Mapped[int] = mapped_column(Integer, ForeignKey("trips.id"), nullable=False)
    trip_id_2: Mapped[int] = mapped_column(Integer, ForeignKey("trips.id"), nullable=False)

    # Match scoring (stored as JSON)
    score: Mapped[dict] = mapped_column(JSON, nullable=False)
    llm_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        Enum(MatchStatus), default=MatchStatus.SUGGESTED, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    trip_1: Mapped["Trip"] = relationship("Trip", foreign_keys=[trip_id_1])
    trip_2: Mapped["Trip"] = relationship("Trip", foreign_keys=[trip_id_2])
    connections: Mapped[list["Connection"]] = relationship("Connection", back_populates="match")


class Connection(Base):
    """Connection request model."""

    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), nullable=False)
    initiator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        Enum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="connections")
    initiator: Mapped["User"] = relationship("User", foreign_keys=[initiator_id])


class Feedback(Base):
    """Feedback model."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    feedback_type: Mapped[str] = mapped_column(Enum(FeedbackType), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional references
    match_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("matches.id"), nullable=True)
    reported_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    report_reason: Mapped[str | None] = mapped_column(Enum(ReportReason), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="feedback_given", foreign_keys=[user_id])


class Experiment(Base):
    """Experiment tracking model."""

    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variant: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Conversion tracking
    converted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ExperimentEvent(Base):
    """
    Event log for the UX flow A/B/C experiment.

    Stores one row per user action (profile_completed, parse_accepted, etc.).
    user_id is a plain string so it works with both session UUIDs and synthetic IDs.
    metadata_ uses a trailing underscore to avoid clashing with SQLAlchemy internals.
    """

    __tablename__ = "experiment_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    variant: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metadata_: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
