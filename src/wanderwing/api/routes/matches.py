"""Match-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wanderwing.api.dependencies import get_current_user_id, get_match_service
from wanderwing.schemas.match import Match, MatchWithTrips
from wanderwing.services import MatchService

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/trips/{trip_id}", response_model=list[MatchWithTrips])
async def find_matches(
    trip_id: int,
    min_score: float = Query(default=0.5, ge=0.0, le=1.0),
    user_id: int = Depends(get_current_user_id),
    match_service: MatchService = Depends(get_match_service),
) -> list[MatchWithTrips]:
    """Find compatible travelers for a trip."""
    return await match_service.find_matches_for_trip(trip_id, min_score)


@router.get("/{match_id}", response_model=Match)
async def get_match(
    match_id: int,
    match_service: MatchService = Depends(get_match_service),
) -> Match:
    """Get match details by ID."""
    match = match_service.get_match(match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {match_id} not found",
        )
    return match


@router.get("/trips/{trip_id}", response_model=list[Match])
async def list_trip_matches(
    trip_id: int,
    match_service: MatchService = Depends(get_match_service),
) -> list[Match]:
    """List all matches for a trip."""
    return match_service.list_matches_for_trip(trip_id)
