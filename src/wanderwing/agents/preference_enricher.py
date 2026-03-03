"""Preference enrichment agent - enhances trip data with implicit preferences."""

from wanderwing.llm import get_llm_client
from wanderwing.schemas.trip import ParsedItinerary
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


async def enrich_preferences(parsed_itinerary: ParsedItinerary) -> ParsedItinerary:
    """
    Enrich trip preferences with implied interests and suggestions.

    This agent takes a basic parsed itinerary and infers additional preferences
    based on the stated activities and destination.

    Args:
        parsed_itinerary: Initially parsed itinerary

    Returns:
        Enhanced ParsedItinerary with additional inferred preferences
    """
    logger.info(f"Enriching preferences for {parsed_itinerary.destination}")

    # For MVP, this is a placeholder that returns the input unchanged
    # In Phase 2-3, this would:
    # 1. Analyze stated activities
    # 2. Infer additional compatible activities
    # 3. Suggest budget tier if not specified
    # 4. Recommend accommodation types based on travel style

    # TODO: Implement LLM-based preference enrichment
    # Example prompt: "Given this trip to {destination} with activities {activities},
    # what other activities might this traveler enjoy? What budget tier does this suggest?"

    return parsed_itinerary


async def ask_clarifying_questions(parsed_itinerary: ParsedItinerary) -> list[str]:
    """
    Generate clarifying questions for ambiguous trip details.

    Args:
        parsed_itinerary: Parsed itinerary with potential ambiguities

    Returns:
        List of questions to ask the user
    """
    questions = []

    if not parsed_itinerary.start_date:
        questions.append("When are you planning to travel? (approximate dates are fine)")

    if not parsed_itinerary.duration_days:
        questions.append("How long is your trip?")

    if not parsed_itinerary.activities:
        questions.append("What activities interest you most?")

    if parsed_itinerary.ambiguities:
        for ambiguity in parsed_itinerary.ambiguities:
            questions.append(f"Can you clarify: {ambiguity}")

    return questions
