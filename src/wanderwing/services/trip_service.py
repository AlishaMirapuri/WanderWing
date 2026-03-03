"""Trip service - handles trip creation and itinerary extraction."""

from sqlalchemy.orm import Session

from wanderwing.agents import extract_itinerary
from wanderwing.db.repositories import TripRepository
from wanderwing.schemas.trip import Trip, TripCreate, TripUpdate
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class TripService:
    """Service for trip operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.trip_repo = TripRepository(db)

    async def create_trip(self, user_id: int, trip_data: TripCreate) -> Trip:
        """
        Create a new trip with itinerary extraction.

        Args:
            user_id: User creating the trip
            trip_data: Trip creation data

        Returns:
            Created trip with parsed itinerary
        """
        logger.info(f"Creating trip for user {user_id}")

        # Extract itinerary from natural language input
        try:
            parsed_itinerary = await extract_itinerary(trip_data.raw_input)
            trip_data.parsed_data = parsed_itinerary
        except Exception as e:
            logger.error(f"Failed to extract itinerary: {e}")
            # Create trip without parsed data for now
            trip_data.parsed_data = None

        # Save to database
        trip_model = self.trip_repo.create(user_id, trip_data)
        return Trip.model_validate(trip_model)

    def get_trip(self, trip_id: int) -> Trip | None:
        """Get trip by ID."""
        trip_model = self.trip_repo.get_by_id(trip_id)
        if not trip_model:
            return None
        return Trip.model_validate(trip_model)

    def update_trip(self, trip_id: int, trip_data: TripUpdate) -> Trip | None:
        """Update a trip."""
        trip_model = self.trip_repo.update(trip_id, trip_data)
        if not trip_model:
            return None
        return Trip.model_validate(trip_model)

    def list_user_trips(self, user_id: int) -> list[Trip]:
        """List all trips for a user."""
        trip_models = self.trip_repo.list_by_user(user_id)
        return [Trip.model_validate(t) for t in trip_models]

    def list_active_trips(self, skip: int = 0, limit: int = 100) -> list[Trip]:
        """List all active trips."""
        trip_models = self.trip_repo.list_active_trips(skip, limit)
        return [Trip.model_validate(t) for t in trip_models]
