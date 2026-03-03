"""Feedback-related API endpoints."""

from fastapi import APIRouter, Depends, status

from wanderwing.api.dependencies import get_current_user_id, get_db
from wanderwing.db import FeedbackRepository
from wanderwing.schemas.feedback import Feedback, FeedbackCreate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=Feedback, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Feedback:
    """Submit feedback, rating, or report."""
    feedback_repo = FeedbackRepository(db)
    feedback_model = feedback_repo.create(user_id, feedback_data)
    return Feedback.model_validate(feedback_model)


@router.get("/matches/{match_id}", response_model=list[Feedback])
async def get_match_feedback(
    match_id: int,
    db: Session = Depends(get_db),
) -> list[Feedback]:
    """Get all feedback for a match."""
    feedback_repo = FeedbackRepository(db)
    feedback_models = feedback_repo.get_match_ratings(match_id)
    return [Feedback.model_validate(f) for f in feedback_models]
