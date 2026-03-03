"""User service - handles user operations."""

from sqlalchemy.orm import Session

from wanderwing.db.repositories import UserRepository
from wanderwing.schemas.user import User, UserCreate
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing = self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ValueError(f"User with email {user_data.email} already exists")

        user_model = self.user_repo.create(user_data)
        return User.model_validate(user_model)

    def get_user(self, user_id: int) -> User | None:
        """Get user by ID."""
        user_model = self.user_repo.get_by_id(user_id)
        if not user_model:
            return None
        return User.model_validate(user_model)

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        user_model = self.user_repo.get_by_email(email)
        if not user_model:
            return None
        return User.model_validate(user_model)
