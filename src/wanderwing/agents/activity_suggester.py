"""Activity suggestion agent - recommends shared activities for matched travelers."""

from pathlib import Path

from wanderwing.llm import get_llm_client
from wanderwing.schemas.trip import ParsedItinerary
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


async def suggest_activities(
    trip_1: ParsedItinerary,
    trip_2: ParsedItinerary,
) -> list[str]:
    """
    Suggest shared activities for two matched travelers.

    Args:
        trip_1: First traveler's itinerary
        trip_2: Second traveler's itinerary

    Returns:
        List of suggested shared activities
    """
    logger.info(
        f"Suggesting activities for {trip_1.destination} + {trip_2.destination}"
    )

    # Find common activities
    common_activities = set(trip_1.activities) & set(trip_2.activities)

    if common_activities:
        # Return common activities as suggestions
        suggestions = [act.value for act in common_activities]
        logger.info(f"Found {len(suggestions)} common activities")
        return suggestions

    # If no common activities, suggest based on destination
    # For MVP, return placeholder suggestions
    # TODO: Implement LLM-based activity suggestions
    suggestions = [
        "Explore local cuisine together",
        "Visit popular landmarks",
        "Share transportation costs",
    ]

    return suggestions


async def generate_activity_description(
    activity: str,
    destination: str,
) -> str:
    """
    Generate a description for a suggested activity.

    Args:
        activity: Activity name
        destination: Destination location

    Returns:
        Human-readable activity description
    """
    # Placeholder implementation
    # TODO: Use LLM to generate engaging activity descriptions
    return f"Enjoy {activity} in {destination}"
