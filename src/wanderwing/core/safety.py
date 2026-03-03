"""Safety and trust features - blocking, reporting, verification."""

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from wanderwing.db import models
from wanderwing.schemas.feedback import ReportReason
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class SafetyFilter:
    """Safety filtering and moderation."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def is_user_blocked(self, user_id: int, other_user_id: int) -> bool:
        """Check if user has blocked another user."""
        # For MVP, we'll store blocks in feedback table with report_reason
        # In production, consider a dedicated blocks table
        result = self.db.execute(
            select(models.Feedback).where(
                and_(
                    models.Feedback.user_id == user_id,
                    models.Feedback.reported_user_id == other_user_id,
                    models.Feedback.report_reason == ReportReason.HARASSMENT,
                )
            )
        ).first()

        return result is not None

    def block_user(self, blocker_id: int, blocked_id: int, reason: str) -> None:
        """Block a user."""
        feedback = models.Feedback(
            user_id=blocker_id,
            reported_user_id=blocked_id,
            feedback_type="report",
            report_reason=ReportReason.HARASSMENT,
            comment=reason,
        )
        self.db.add(feedback)
        self.db.commit()
        logger.info(f"User {blocker_id} blocked user {blocked_id}")

    def get_reported_users(self, threshold: int = 3) -> list[int]:
        """Get user IDs with reports above threshold."""
        # This would aggregate reports per user
        # For MVP, simplified implementation
        return []


def check_user_blocked(db: Session, user_id: int, other_user_id: int) -> bool:
    """
    Check if two users have blocked each other.

    Args:
        db: Database session
        user_id: First user ID
        other_user_id: Second user ID

    Returns:
        True if either user has blocked the other
    """
    safety_filter = SafetyFilter(db)
    return safety_filter.is_user_blocked(
        user_id, other_user_id
    ) or safety_filter.is_user_blocked(other_user_id, user_id)


def verify_user_eligibility(user: models.User) -> tuple[bool, str | None]:
    """
    Check if user is eligible for matching.

    Args:
        user: User model

    Returns:
        Tuple of (is_eligible, reason_if_not)
    """
    if not user.is_active:
        return False, "Account is inactive"

    # In production, add more checks:
    # - Email verification
    # - Profile completeness
    # - Recent activity

    return True, None
