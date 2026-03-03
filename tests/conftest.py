"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wanderwing.db.base import Base


@pytest.fixture
def db_session() -> Session:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_llm_response() -> dict:
    """Mock LLM response for testing."""
    return {
        "destination": "Tokyo",
        "secondary_destinations": [],
        "start_date": "2024-04-01",
        "end_date": "2024-04-10",
        "duration_days": 10,
        "activities": ["hiking", "food_tour", "sightseeing"],
        "budget_tier": "moderate",
        "travel_style": ["adventure", "culture"],
        "flexibility_days": 2,
        "accommodation_type": "hostel",
        "group_size_preference": "solo",
        "confidence_score": 0.9,
        "ambiguities": [],
    }
