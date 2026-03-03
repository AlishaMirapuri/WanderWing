"""Data access layer for database operations."""

from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from wanderwing.schemas.feedback import FeedbackCreate
from wanderwing.schemas.match import ConnectionCreate, MatchCreate
from wanderwing.schemas.trip import TripCreate, TripStatus, TripUpdate
from wanderwing.schemas.user import UserCreate

from . import models


class UserRepository:
    """Repository for user operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_data: UserCreate) -> models.User:
        """Create a new user."""
        # TODO: Hash password properly
        user = models.User(
            email=user_data.email,
            name=user_data.name,
            bio=user_data.bio,
            hashed_password=f"hashed_{user_data.password}",  # Placeholder
            travel_styles=[style.value for style in user_data.travel_styles],
            budget_tier=user_data.budget_tier.value,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> models.User | None:
        """Get user by ID."""
        return self.db.get(models.User, user_id)

    def get_by_email(self, email: str) -> models.User | None:
        """Get user by email."""
        return self.db.execute(
            select(models.User).where(models.User.email == email)
        ).scalar_one_or_none()

    def list_active_users(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        """List active users."""
        return list(
            self.db.execute(
                select(models.User)
                .where(models.User.is_active == True)  # noqa: E712
                .offset(skip)
                .limit(limit)
            ).scalars()
        )


class TripRepository:
    """Repository for trip operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_id: int, trip_data: TripCreate) -> models.Trip:
        """Create a new trip."""
        trip = models.Trip(
            user_id=user_id,
            raw_input=trip_data.raw_input,
            parsed_data=trip_data.parsed_data.model_dump() if trip_data.parsed_data else None,
            status=TripStatus.ACTIVE,
        )
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def get_by_id(self, trip_id: int) -> models.Trip | None:
        """Get trip by ID."""
        return self.db.get(models.Trip, trip_id)

    def update(self, trip_id: int, trip_data: TripUpdate) -> models.Trip | None:
        """Update a trip."""
        trip = self.get_by_id(trip_id)
        if not trip:
            return None

        if trip_data.parsed_data:
            trip.parsed_data = trip_data.parsed_data.model_dump()
        if trip_data.status:
            trip.status = trip_data.status

        self.db.commit()
        self.db.refresh(trip)
        return trip

    def list_by_user(self, user_id: int) -> list[models.Trip]:
        """List trips for a user."""
        return list(
            self.db.execute(
                select(models.Trip).where(models.Trip.user_id == user_id)
            ).scalars()
        )

    def list_active_trips(self, skip: int = 0, limit: int = 100) -> list[models.Trip]:
        """List all active trips."""
        return list(
            self.db.execute(
                select(models.Trip)
                .where(models.Trip.status == TripStatus.ACTIVE)
                .offset(skip)
                .limit(limit)
            ).scalars()
        )


class MatchRepository:
    """Repository for match operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, match_data: MatchCreate) -> models.Match:
        """Create a new match."""
        match = models.Match(
            trip_id_1=match_data.trip_id_1,
            trip_id_2=match_data.trip_id_2,
            score=match_data.score.model_dump(),
            llm_reasoning=match_data.llm_reasoning,
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_by_id(self, match_id: int) -> models.Match | None:
        """Get match by ID."""
        return self.db.get(models.Match, match_id)

    def list_for_trip(self, trip_id: int, min_score: float = 0.5) -> list[models.Match]:
        """List matches for a trip above minimum score."""
        return list(
            self.db.execute(
                select(models.Match)
                .where(
                    or_(
                        models.Match.trip_id_1 == trip_id,
                        models.Match.trip_id_2 == trip_id,
                    )
                )
                # TODO: Filter by score from JSON field
            ).scalars()
        )

    def exists(self, trip_id_1: int, trip_id_2: int) -> bool:
        """Check if match already exists between two trips."""
        result = self.db.execute(
            select(models.Match).where(
                or_(
                    and_(
                        models.Match.trip_id_1 == trip_id_1,
                        models.Match.trip_id_2 == trip_id_2,
                    ),
                    and_(
                        models.Match.trip_id_1 == trip_id_2,
                        models.Match.trip_id_2 == trip_id_1,
                    ),
                )
            )
        ).first()
        return result is not None


class ConnectionRepository:
    """Repository for connection operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, connection_data: ConnectionCreate) -> models.Connection:
        """Create a new connection request."""
        connection = models.Connection(
            match_id=connection_data.match_id,
            initiator_id=connection_data.initiator_id,
            message=connection_data.message,
        )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def get_by_id(self, connection_id: int) -> models.Connection | None:
        """Get connection by ID."""
        return self.db.get(models.Connection, connection_id)

    def list_for_user(self, user_id: int) -> list[models.Connection]:
        """List connections for a user."""
        return list(
            self.db.execute(
                select(models.Connection).where(
                    models.Connection.initiator_id == user_id
                )
            ).scalars()
        )


class FeedbackRepository:
    """Repository for feedback operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_id: int, feedback_data: FeedbackCreate) -> models.Feedback:
        """Create new feedback."""
        feedback = models.Feedback(
            user_id=user_id,
            feedback_type=feedback_data.feedback_type,
            rating=feedback_data.rating,
            comment=feedback_data.comment,
            match_id=feedback_data.match_id,
            reported_user_id=feedback_data.reported_user_id,
            report_reason=feedback_data.report_reason,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_match_ratings(self, match_id: int) -> list[models.Feedback]:
        """Get all ratings for a match."""
        return list(
            self.db.execute(
                select(models.Feedback).where(models.Feedback.match_id == match_id)
            ).scalars()
        )
