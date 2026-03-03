"""Connection-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from wanderwing.api.dependencies import get_current_user_id, get_match_service
from wanderwing.schemas.match import Connection, ConnectionCreate
from wanderwing.services import MatchService

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("", response_model=Connection, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    user_id: int = Depends(get_current_user_id),
    match_service: MatchService = Depends(get_match_service),
) -> Connection:
    """Create a connection request with a matched traveler."""
    # Verify the user is part of this match
    match = match_service.get_match(connection_data.match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {connection_data.match_id} not found",
        )

    return match_service.create_connection(connection_data)


@router.get("/{connection_id}", response_model=Connection)
async def get_connection(
    connection_id: int,
    match_service: MatchService = Depends(get_match_service),
) -> Connection:
    """Get connection details."""
    connection = match_service.get_connection(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )
    return connection


@router.get("", response_model=list[Connection])
async def list_my_connections(
    user_id: int = Depends(get_current_user_id),
    match_service: MatchService = Depends(get_match_service),
) -> list[Connection]:
    """List all connections for the current user."""
    return match_service.list_user_connections(user_id)
