"""Intent parsing API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from wanderwing.api.dependencies import get_current_user_id
from wanderwing.schemas.trip_enhanced import TripIntentRequest, TripIntentResponse

router = APIRouter(prefix="/parse-intent", tags=["intent-parsing"])


@router.post("", response_model=TripIntentResponse, status_code=status.HTTP_200_OK)
async def parse_traveler_intent(
    request: TripIntentRequest,
    user_id: int = Depends(get_current_user_id),
) -> TripIntentResponse:
    """
    Parse traveler intent from natural language input.

    This is the core LLM-powered agent endpoint that converts free-form
    travel descriptions into structured itinerary data.

    The agent will extract:
    - Destinations and multi-city routes
    - Travel dates and duration
    - Accommodation preferences
    - Activities and interests
    - Budget tier
    - Group preferences

    Returns:
    - Structured ParsedTravelerIntent object
    - Confidence score for extraction quality
    - Clarification questions for ambiguous items
    - Suggested edits to improve the plan

    Example input:
    ```
    "Planning a 2-week trip to Japan in April. Want to spend 5 days in Tokyo
    exploring temples and trying street food, then take the bullet train to
    Kyoto for 4 days to see traditional culture. Budget around $150/day.
    Prefer hostels or guesthouses. Love hiking and photography."
    ```

    The agent uses:
    - LLM (GPT-4 or Claude) for intent extraction
    - Few-shot prompting with examples
    - Structured output validation with Pydantic
    - Confidence scoring based on information completeness

    If confidence < 0.7, clarification questions are returned.
    """
    # TODO: Implement intent parsing agent
    # 1. Load appropriate prompt template based on prompt_version
    # 2. Call LLM with structured output
    # 3. Validate extracted data with Pydantic
    # 4. Calculate confidence score
    # 5. Generate clarification questions if needed
    # 6. Track in experiments if A/B testing enabled
    # 7. Log performance metrics (latency, tokens, cost)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Intent parsing not yet implemented. This will use the itinerary extraction agent.",
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
    # 1. Load original parsed intent
    # 2. Apply user refinements
    # 3. Re-validate with Pydantic
    # 4. Update confidence score
    # 5. Track refinement for agent improvement
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Intent refinement not yet implemented",
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
            },
            {
                "title": "Southeast Asia backpacking",
                "input": "3-week budget backpacking trip starting in Bangkok. Want to island hop in Thailand, maybe visit Cambodia for Angkor Wat. Prefer hostels, love beaches and local food. Under $50/day.",
                "complexity": "high",
            },
            {
                "title": "European city break",
                "input": "Long weekend in Paris, April 15-18. Interested in art museums, photography, and good cafes. Mid-range budget, prefer Airbnb in Marais or Latin Quarter.",
                "complexity": "low",
            },
            {
                "title": "Adventure hiking trip",
                "input": "Solo hiking trip to Patagonia in November. Want to do the W Trek and maybe Torres del Paine. 10 days total. Experienced hiker, comfortable camping. Budget-conscious but willing to pay for guided portions.",
                "complexity": "medium",
            },
        ]
    }
