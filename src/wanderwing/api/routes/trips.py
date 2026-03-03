"""Trip-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from wanderwing.api.dependencies import get_current_user_id, get_trip_service
from wanderwing.schemas.trip import Trip, TripCreate, TripUpdate
from wanderwing.services import TripService

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=Trip, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_data: TripCreate,
    user_id: int = Depends(get_current_user_id),
    trip_service: TripService = Depends(get_trip_service),
) -> Trip:
    """Create a new trip with automatic itinerary extraction."""
    return await trip_service.create_trip(user_id, trip_data)


@router.get("/{trip_id}", response_model=Trip)
async def get_trip(
    trip_id: int,
    trip_service: TripService = Depends(get_trip_service),
) -> Trip:
    """Get trip by ID."""
    trip = trip_service.get_trip(trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip {trip_id} not found",
        )
    return trip


@router.patch("/{trip_id}", response_model=Trip)
async def update_trip(
    trip_id: int,
    trip_data: TripUpdate,
    user_id: int = Depends(get_current_user_id),
    trip_service: TripService = Depends(get_trip_service),
) -> Trip:
    """Update a trip."""
    trip = trip_service.update_trip(trip_id, trip_data)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip {trip_id} not found",
        )
    return trip


@router.get("", response_model=list[Trip])
async def list_my_trips(
    user_id: int = Depends(get_current_user_id),
    trip_service: TripService = Depends(get_trip_service),
) -> list[Trip]:
    """List all trips for the current user."""
    return trip_service.list_user_trips(user_id)
