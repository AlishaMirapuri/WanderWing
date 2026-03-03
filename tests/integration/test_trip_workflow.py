"""Integration tests for trip creation workflow."""

import pytest
from unittest.mock import AsyncMock, patch

from wanderwing.db.repositories import TripRepository, UserRepository
from wanderwing.schemas.trip import TripCreate
from wanderwing.schemas.user import BudgetTier, UserCreate
from wanderwing.services.trip_service import TripService


@pytest.mark.asyncio
async def test_full_trip_creation_workflow(db_session, mock_llm_response):
    """Test full trip creation workflow."""
    # Create user
    user_repo = UserRepository(db_session)
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="password123",
        budget_tier=BudgetTier.MODERATE,
    )
    user = user_repo.create(user_data)

    # Mock LLM extraction
    with patch("wanderwing.services.trip_service.extract_itinerary") as mock_extract:
        from wanderwing.schemas.trip import ParsedItinerary

        mock_extract.return_value = ParsedItinerary(**mock_llm_response)

        # Create trip
        trip_service = TripService(db_session)
        trip_data = TripCreate(raw_input="Going to Tokyo for 10 days")

        trip = await trip_service.create_trip(user.id, trip_data)

        assert trip.id is not None
        assert trip.user_id == user.id
        assert trip.parsed_data is not None
        assert trip.parsed_data.destination == "Tokyo"


def test_list_user_trips(db_session):
    """Test listing trips for a user."""
    # Create user
    user_repo = UserRepository(db_session)
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="password123",
    )
    user = user_repo.create(user_data)

    # Create trips
    trip_repo = TripRepository(db_session)
    trip1 = TripCreate(raw_input="Trip 1")
    trip2 = TripCreate(raw_input="Trip 2")

    trip_repo.create(user.id, trip1)
    trip_repo.create(user.id, trip2)

    # List trips
    trip_service = TripService(db_session)
    trips = trip_service.list_user_trips(user.id)

    assert len(trips) == 2
