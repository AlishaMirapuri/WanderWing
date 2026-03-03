"""Intent parsing API endpoints - UPDATED with IntentParser service."""

from fastapi import APIRouter, Depends, HTTPException, status

from wanderwing.api.dependencies import get_current_user_id
from wanderwing.schemas.trip_enhanced import TripIntentRequest, TripIntentResponse
from wanderwing.services.intent_parser import IntentParser, IntentParsingError, get_intent_parser
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/parse-intent", tags=["intent-parsing"])


@router.post("", response_model=TripIntentResponse, status_code=status.HTTP_200_OK)
async def parse_traveler_intent(
    request: TripIntentRequest,
    user_id: int = Depends(get_current_user_id),
    parser: IntentParser = Depends(get_intent_parser),
) -> TripIntentResponse:
    """
    Parse traveler intent from natural language input.

    **Now fully implemented with production-grade LLM parsing!**

    This endpoint uses a sophisticated LLM-powered agent that:
    - Converts natural language to structured ParsedTravelerIntent
    - Handles malformed LLM output with fallback parsing
    - Retries with exponential backoff on failures
    - Validates against business rules
    - Returns confidence scores and clarification questions

    The parser implements:
    - ✅ Three-layer validation (JSON mode, Pydantic, business rules)
    - ✅ Graceful degradation (fallback parser)
    - ✅ Comprehensive logging (tokens, cost, errors)
    - ✅ Prompt versioning (A/B testing ready)
    - ✅ Cost tracking
    - ✅ Quality metrics

    Example input:
    ```
    "I'm going to Lisbon for 4 days, love food markets and live music,
    probably staying near Alfama, not into clubbing, happy to meet
    other solo travelers for brunch or a walking tour"
    ```

    Returns:
    - Structured ParsedTravelerIntent
    - Confidence score (0.0-1.0)
    - Clarification questions if needed
    - Processing time

    See INTENT_PARSER_DESIGN.md for detailed design decisions.
    """
    logger.info(
        "Received intent parsing request",
        extra={
            "user_id": user_id,
            "input_length": len(request.raw_input),
            "prompt_version": request.prompt_version,
        },
    )

    import time
    start_time = time.time()

    try:
        # Parse intent using LLM service
        parsed_intent = await parser.parse(
            raw_input=request.raw_input,
            user_context={"user_id": user_id} if request.user_id else None,
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Determine if clarification needed
        needs_clarification = (
            parsed_intent.confidence_score < 0.7
            or len(parsed_intent.ambiguities) > 2
        )

        # Generate suggested edits based on ambiguities
        suggested_edits = []
        if not parsed_intent.overall_start_date:
            suggested_edits.append("Specify exact travel dates or approximate timeframe")
        if not parsed_intent.budget_total_usd and not parsed_intent.budget_tier:
            suggested_edits.append("Add budget information (per day or total)")
        if len(parsed_intent.destination_stays) == 0:
            suggested_edits.append("Provide destination city or country")
        if len(parsed_intent.activities) == 0:
            suggested_edits.append("Mention activities or interests")

        logger.info(
            "Intent parsing completed",
            extra={
                "user_id": user_id,
                "destination": parsed_intent.primary_destination,
                "confidence": parsed_intent.confidence_score,
                "needs_clarification": needs_clarification,
                "processing_time_ms": processing_time_ms,
            },
        )

        return TripIntentResponse(
            parsed_intent=parsed_intent,
            needs_clarification=needs_clarification,
            suggested_edits=suggested_edits,
            processing_time_ms=processing_time_ms,
        )

    except IntentParsingError as e:
        logger.error(
            "Intent parsing failed",
            extra={
                "user_id": user_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse travel intent: {str(e)}",
        )

    except Exception as e:
        logger.error(
            "Unexpected error in intent parsing",
            extra={
                "user_id": user_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during parsing",
        )


@router.post("/refine", response_model=TripIntentResponse)
async def refine_traveler_intent(
    intent_id: int,
    refinements: dict[str, str],
    user_id: int = Depends(get_current_user_id),
) -> TripIntentResponse:
    """
    Refine a previously parsed intent with user corrections.

    This endpoint allows users to provide clarifications or corrections
    to the initially parsed intent, creating a feedback loop.

    Args:
        intent_id: ID of the previously parsed intent
        refinements: Dict of field -> corrected value

    Returns:
        Updated ParsedTravelerIntent with refinements applied
    """
    # TODO: Implement intent refinement
    # 1. Load original parsed intent from database
    # 2. Apply user refinements
    # 3. Re-parse with LLM if major changes
    # 4. Re-validate with Pydantic
    # 5. Update confidence score
    # 6. Track refinement for agent improvement
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Intent refinement not yet implemented (Phase 2)",
    )


@router.get("/examples")
async def get_example_inputs() -> dict:
    """
    Get example travel descriptions for user guidance.

    Returns a list of example inputs that work well with the parser,
    helping users understand how to describe their trips effectively.
    """
    return {
        "examples": [
            {
                "title": "Multi-city Japan trip",
                "input": "Planning a 2-week trip to Japan in April. Want to spend 5 days in Tokyo, then bullet train to Kyoto for 4 days, and finish with 3 days in Osaka. Love hiking, food tours, and temples. Budget around $150/day.",
                "complexity": "medium",
                "expected_confidence": 0.9,
            },
            {
                "title": "Vague Lisbon weekend",
                "input": "Thinking about Lisbon for a long weekend sometime next month. Love food markets and live music. Not into clubbing.",
                "complexity": "low",
                "expected_confidence": 0.65,
                "note": "Will generate clarification questions for dates and budget",
            },
            {
                "title": "Southeast Asia backpacking",
                "input": "3-week budget backpacking trip starting in Bangkok. Want to island hop in Thailand, maybe visit Cambodia for Angkor Wat. Prefer hostels, love beaches and local food. Under $50/day.",
                "complexity": "high",
                "expected_confidence": 0.75,
            },
            {
                "title": "European city break",
                "input": "Long weekend in Paris, April 15-18. Interested in art museums, photography, and good cafes. Mid-range budget, prefer Airbnb in Marais or Latin Quarter.",
                "complexity": "low",
                "expected_confidence": 0.95,
                "note": "Complete information, should parse perfectly",
            },
        ],
        "tips": [
            "Include destination city or country",
            "Mention travel dates or duration",
            "List activities or interests",
            "Specify budget range or tier",
            "Note accommodation preferences if important",
        ],
        "parser_capabilities": {
            "multi_city_trips": True,
            "date_inference": True,
            "budget_tier_classification": True,
            "activity_extraction": True,
            "confidence_scoring": True,
            "clarification_questions": True,
        },
    }
