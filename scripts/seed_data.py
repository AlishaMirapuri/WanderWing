"""Seed database with test data."""

import asyncio
from datetime import date, datetime

from wanderwing.db import SessionLocal, User
from wanderwing.db.repositories import TripRepository, UserRepository
from wanderwing.schemas.trip import ActivityType, ParsedItinerary, TripCreate
from wanderwing.schemas.user import BudgetTier, TravelStyle, UserCreate


def seed_users(db) -> list[User]:
    """Create test users."""
    user_repo = UserRepository(db)
    users = []

    test_users = [
        UserCreate(
            email="alice@example.com",
            name="Alice Chen",
            bio="Digital nomad who loves adventure travel",
            password="password123",
            travel_styles=[TravelStyle.ADVENTURE, TravelStyle.NATURE],
            budget_tier=BudgetTier.MODERATE,
        ),
        UserCreate(
            email="bob@example.com",
            name="Bob Martinez",
            bio="Food enthusiast and culture explorer",
            password="password123",
            travel_styles=[TravelStyle.FOOD, TravelStyle.CULTURE],
            budget_tier=BudgetTier.COMFORTABLE,
        ),
        UserCreate(
            email="carol@example.com",
            name="Carol Kim",
            bio="Budget backpacker seeking authentic experiences",
            password="password123",
            travel_styles=[TravelStyle.BUDGET, TravelStyle.CULTURE],
            budget_tier=BudgetTier.BUDGET,
        ),
        UserCreate(
            email="david@example.com",
            name="David Thompson",
            bio="Luxury traveler who enjoys relaxation",
            password="password123",
            travel_styles=[TravelStyle.LUXURY, TravelStyle.RELAXATION],
            budget_tier=BudgetTier.LUXURY,
        ),
        UserCreate(
            email="emma@example.com",
            name="Emma Wilson",
            bio="Solo traveler interested in hiking and photography",
            password="password123",
            travel_styles=[TravelStyle.ADVENTURE, TravelStyle.NATURE],
            budget_tier=BudgetTier.MODERATE,
        ),
    ]

    for user_data in test_users:
        try:
            user = user_repo.create(user_data)
            users.append(user)
            print(f"Created user: {user.name}")
        except Exception as e:
            print(f"User {user_data.email} already exists or error: {e}")

    return users


def seed_trips(db, users: list[User]) -> None:
    """Create test trips."""
    trip_repo = TripRepository(db)

    test_trips = [
        (
            users[0].id,
            TripCreate(
                raw_input="2-week trip to Japan in April, love hiking and food tours",
                parsed_data=ParsedItinerary(
                    destination="Tokyo",
                    start_date=date(2024, 4, 1),
                    end_date=date(2024, 4, 14),
                    duration_days=14,
                    activities=[
                        ActivityType.HIKING,
                        ActivityType.FOOD_TOUR,
                        ActivityType.SIGHTSEEING,
                    ],
                    budget_tier="moderate",
                    travel_style=["adventure", "culture"],
                    confidence_score=0.9,
                ),
            ),
        ),
        (
            users[1].id,
            TripCreate(
                raw_input="Going to Tokyo for 10 days, interested in food and culture",
                parsed_data=ParsedItinerary(
                    destination="Tokyo",
                    start_date=date(2024, 4, 5),
                    end_date=date(2024, 4, 15),
                    duration_days=10,
                    activities=[ActivityType.FOOD_TOUR, ActivityType.MUSEUMS, ActivityType.SIGHTSEEING],
                    budget_tier="comfortable",
                    travel_style=["food", "culture"],
                    confidence_score=0.95,
                ),
            ),
        ),
        (
            users[2].id,
            TripCreate(
                raw_input="Budget backpacking in Southeast Asia, starting in Bangkok",
                parsed_data=ParsedItinerary(
                    destination="Bangkok",
                    start_date=date(2024, 5, 1),
                    end_date=date(2024, 5, 21),
                    duration_days=21,
                    activities=[
                        ActivityType.LOCAL_EXPERIENCES,
                        ActivityType.FOOD_TOUR,
                        ActivityType.BEACH,
                    ],
                    budget_tier="budget",
                    travel_style=["budget", "culture"],
                    confidence_score=0.85,
                ),
            ),
        ),
        (
            users[3].id,
            TripCreate(
                raw_input="Luxury resort stay in Bali for relaxation and spa",
                parsed_data=ParsedItinerary(
                    destination="Bali",
                    start_date=date(2024, 6, 10),
                    end_date=date(2024, 6, 17),
                    duration_days=7,
                    activities=[ActivityType.RELAXATION, ActivityType.BEACH],
                    budget_tier="luxury",
                    travel_style=["luxury", "relaxation"],
                    confidence_score=0.9,
                ),
            ),
        ),
        (
            users[4].id,
            TripCreate(
                raw_input="Solo trip to Paris for art museums and photography",
                parsed_data=ParsedItinerary(
                    destination="Paris",
                    start_date=date(2024, 5, 15),
                    end_date=date(2024, 5, 22),
                    duration_days=7,
                    activities=[ActivityType.MUSEUMS, ActivityType.PHOTOGRAPHY, ActivityType.SIGHTSEEING],
                    budget_tier="moderate",
                    travel_style=["culture"],
                    confidence_score=0.88,
                ),
            ),
        ),
    ]

    for user_id, trip_data in test_trips:
        try:
            trip = trip_repo.create(user_id, trip_data)
            print(f"Created trip: {trip.parsed_data['destination']} for user {user_id}")
        except Exception as e:
            print(f"Error creating trip: {e}")


def main() -> None:
    """Main seeding function."""
    print("Seeding database with test data...")

    db = SessionLocal()
    try:
        # Seed users
        users = seed_users(db)

        # Seed trips
        if users:
            seed_trips(db, users)

        print("\nDatabase seeded successfully!")
        print(f"Created {len(users)} users")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
