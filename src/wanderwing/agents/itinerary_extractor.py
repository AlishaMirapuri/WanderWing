"""Itinerary extraction agent - converts natural language to structured trip data."""

from pathlib import Path

from wanderwing.llm import get_llm_client
from wanderwing.schemas.trip import ParsedItinerary
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"


async def extract_itinerary(user_input: str) -> ParsedItinerary:
    """
    Extract structured itinerary from natural language input.

    Args:
        user_input: User's natural language trip description

    Returns:
        ParsedItinerary object with extracted information

    Raises:
        ValueError: If extraction fails or produces invalid data
    """
    logger.info(f"Extracting itinerary from input: {user_input[:100]}...")

    # Load prompt template
    prompt_template = (PROMPTS_DIR / "extraction_v1.txt").read_text()
    prompt = prompt_template.format(user_input=user_input)

    try:
        # Call LLM
        llm_client = get_llm_client()
        result = await llm_client.complete_structured(
            prompt=prompt,
            response_model=ParsedItinerary,
            temperature=0.1,
        )

        if isinstance(result, ParsedItinerary):
            logger.info(
                f"Successfully extracted itinerary: {result.destination}",
                extra={"confidence": result.confidence_score},
            )
            return result
        else:
            # Fallback if response_model not supported
            return ParsedItinerary.model_validate(result)

    except Exception as e:
        logger.error(f"Failed to extract itinerary: {e}")
        raise ValueError(f"Could not parse trip information: {e}") from e


async def validate_extraction(parsed: ParsedItinerary) -> tuple[bool, list[str]]:
    """
    Validate extracted itinerary and return issues.

    Args:
        parsed: Extracted itinerary data

    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    errors = []

    if not parsed.destination:
        errors.append("Missing destination")

    if parsed.start_date and parsed.end_date:
        if parsed.start_date > parsed.end_date:
            errors.append("Start date is after end date")

    if parsed.confidence_score < 0.5:
        errors.append("Low confidence in extraction - please clarify details")

    is_valid = len(errors) == 0
    return is_valid, errors
