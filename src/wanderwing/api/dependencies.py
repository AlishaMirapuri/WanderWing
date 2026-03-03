"""FastAPI dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from wanderwing.db import get_db
from wanderwing.services import MatchService, TripService, UserService


def get_trip_service(db: Session = Depends(get_db)) -> TripService:
    """Get trip service instance."""
    return TripService(db)


def get_match_service(db: Session = Depends(get_db)) -> MatchService:
    """Get match service instance."""
    return MatchService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service instance."""
    return UserService(db)


async def get_current_user_id(
    x_user_id: Annotated[int | None, Header()] = None,
) -> int:
    """
    Get current user ID from header.

    For MVP, we use a simple header-based auth.
    In production, replace with proper JWT/OAuth authentication.
    """
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    return x_user_id
