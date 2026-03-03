"""Match service - handles matching and connections."""

from sqlalchemy.orm import Session

from wanderwing.agents import suggest_activities
from wanderwing.core.matching import MatchingEngine
from wanderwing.db.repositories import ConnectionRepository, MatchRepository, TripRepository
from wanderwing.schemas.match import Connection, ConnectionCreate, Match, MatchCreate, MatchWithTrips
from wanderwing.schemas.trip import ParsedItinerary
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class MatchService:
    """Service for matching and connection operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.match_repo = MatchRepository(db)
        self.trip_repo = TripRepository(db)
        self.connection_repo = ConnectionRepository(db)
        self.matching_engine = MatchingEngine(db)

    async def find_matches_for_trip(
        self,
        trip_id: int,
        min_score: float = 0.5,
    ) -> list[MatchWithTrips]:
        """
        Find and create matches for a trip.

        Args:
            trip_id: Trip to find matches for
            min_score: Minimum match score threshold

        Returns:
            List of matches with trip details
        """
        logger.info(f"Finding matches for trip {trip_id}")

        # Use matching engine to find compatible trips
        matches = await self.matching_engine.find_matches_for_trip(trip_id, min_score)

        result = []
        for matched_trip_id, score in matches:
            # Check if match already exists
            if self.match_repo.exists(trip_id, matched_trip_id):
                logger.debug(f"Match already exists: {trip_id} <-> {matched_trip_id}")
                continue

            # Get trip details
            trip = self.trip_repo.get_by_id(trip_id)
            matched_trip = self.trip_repo.get_by_id(matched_trip_id)

            if not trip or not matched_trip:
                continue

            # Create match record
            match_data = MatchCreate(
                trip_id_1=trip_id,
                trip_id_2=matched_trip_id,
                score=score,
            )
            match_model = self.match_repo.create(match_data)

            # Suggest shared activities
            if trip.parsed_data and matched_trip.parsed_data:
                trip_data = ParsedItinerary.model_validate(trip.parsed_data)
                matched_data = ParsedItinerary.model_validate(matched_trip.parsed_data)
                suggested = await suggest_activities(trip_data, matched_data)
            else:
                suggested = []

            # Build response
            match_with_trips = MatchWithTrips(
                **match_model.__dict__,
                trip_1_destination=trip_data.destination if trip.parsed_data else "Unknown",
                trip_2_destination=matched_data.destination if matched_trip.parsed_data else "Unknown",
                trip_1_user_name=trip.user.name,
                trip_2_user_name=matched_trip.user.name,
                suggested_activities=suggested,
            )
            result.append(match_with_trips)

        logger.info(f"Found {len(result)} matches for trip {trip_id}")
        return result

    def get_match(self, match_id: int) -> Match | None:
        """Get match by ID."""
        match_model = self.match_repo.get_by_id(match_id)
        if not match_model:
            return None
        return Match.model_validate(match_model)

    def list_matches_for_trip(self, trip_id: int) -> list[Match]:
        """List all matches for a trip."""
        match_models = self.match_repo.list_for_trip(trip_id)
        return [Match.model_validate(m) for m in match_models]

    def create_connection(self, connection_data: ConnectionCreate) -> Connection:
        """Create a connection request between matched travelers."""
        connection_model = self.connection_repo.create(connection_data)
        logger.info(f"Created connection request for match {connection_data.match_id}")
        return Connection.model_validate(connection_model)

    def get_connection(self, connection_id: int) -> Connection | None:
        """Get connection by ID."""
        connection_model = self.connection_repo.get_by_id(connection_id)
        if not connection_model:
            return None
        return Connection.model_validate(connection_model)

    def list_user_connections(self, user_id: int) -> list[Connection]:
        """List connections for a user."""
        connection_models = self.connection_repo.list_for_user(user_id)
        return [Connection.model_validate(c) for c in connection_models]
