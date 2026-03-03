"""
LLM-powered intent parsing service.

Converts natural language travel descriptions into structured ParsedTravelerIntent objects.
Implements production patterns: retry logic, fallback parsing, validation, error handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from wanderwing.llm import get_llm_client
from wanderwing.schemas.trip_enhanced import ParsedTravelerIntent
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "agents" / "prompts"


class IntentParsingError(Exception):
    """Raised when intent parsing fails completely."""

    pass


class IntentParser:
    """
    Service for parsing natural language travel intent into structured data.

    Design Decisions:
    1. **Strict JSON Mode**: Enforces structured output from LLM
    2. **Fallback Parser**: Handles partial/malformed LLM responses
    3. **Retry Logic**: 3 attempts with exponential backoff
    4. **Validation Pipeline**: LLM output → Pydantic → Business rules
    5. **Prompt Versioning**: Supports A/B testing different prompts
    """

    def __init__(self, prompt_version: str = "v2") -> None:
        """
        Initialize intent parser.

        Args:
            prompt_version: Version of prompt template to use (v1, v2, etc.)
        """
        self.llm_client = get_llm_client()
        self.prompt_version = prompt_version
        self.prompt_template = self._load_prompt_template(prompt_version)

    def _load_prompt_template(self, version: str) -> str:
        """Load prompt template from file."""
        prompt_path = PROMPTS_DIR / f"intent_extraction_{version}.txt"
        if not prompt_path.exists():
            logger.warning(
                f"Prompt version {version} not found, falling back to v1",
                extra={"prompt_version": version},
            )
            prompt_path = PROMPTS_DIR / "intent_extraction_v1.txt"

        return prompt_path.read_text()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((json.JSONDecodeError, ValidationError)),
        reraise=True,
    )
    async def parse(
        self,
        raw_input: str,
        user_context: dict[str, Any] | None = None,
    ) -> ParsedTravelerIntent:
        """
        Parse natural language travel description into structured intent.

        This is the main entry point with full retry logic and error handling.

        Args:
            raw_input: User's natural language trip description
            user_context: Optional context (user preferences, past trips, etc.)

        Returns:
            ParsedTravelerIntent with structured trip data

        Raises:
            IntentParsingError: If parsing fails after all retries
        """
        logger.info(
            "Starting intent parsing",
            extra={
                "input_length": len(raw_input),
                "prompt_version": self.prompt_version,
            },
        )

        try:
            # Build prompt with context
            prompt = self._build_prompt(raw_input, user_context)

            # Call LLM with structured output
            llm_response = await self.llm_client.complete(
                prompt=prompt,
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000,
                response_format="json",
            )

            # Parse and validate
            parsed_intent = await self._parse_and_validate(
                llm_response.content,
                raw_input,
            )

            logger.info(
                "Intent parsing successful",
                extra={
                    "destination": parsed_intent.primary_destination,
                    "confidence": parsed_intent.confidence_score,
                    "llm_tokens": llm_response.tokens_used,
                    "llm_cost": llm_response.cost_usd,
                },
            )

            return parsed_intent

        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(
                "LLM output validation failed, attempting fallback",
                extra={"error": str(e), "attempt": "retry"},
            )
            raise  # Retry will catch this

        except Exception as e:
            logger.error(
                "Intent parsing failed",
                extra={"error": str(e), "error_type": type(e).__name__},
            )
            raise IntentParsingError(f"Failed to parse intent: {e}") from e

    def _build_prompt(
        self,
        raw_input: str,
        user_context: dict[str, Any] | None = None,
    ) -> str:
        """
        Build complete prompt with user input and context.

        Args:
            raw_input: User's description
            user_context: Optional user preferences/history

        Returns:
            Formatted prompt string
        """
        # Add user context if available
        context_section = ""
        if user_context:
            context_section = "\n\nUser Context:\n"
            if "preferred_budget" in user_context:
                context_section += f"- Typical budget: {user_context['preferred_budget']}\n"
            if "travel_styles" in user_context:
                context_section += f"- Travel styles: {', '.join(user_context['travel_styles'])}\n"

        # Format prompt
        prompt = self.prompt_template.format(
            user_input=raw_input,
            context=context_section,
        )

        return prompt

    async def _parse_and_validate(
        self,
        llm_output: str,
        raw_input: str,
    ) -> ParsedTravelerIntent:
        """
        Parse LLM JSON output and validate with Pydantic.

        Implements fallback parser for partial/malformed output.

        Args:
            llm_output: JSON string from LLM
            raw_input: Original user input (for fallback)

        Returns:
            Validated ParsedTravelerIntent

        Raises:
            ValidationError: If validation fails completely
        """
        try:
            # Parse JSON
            parsed_json = json.loads(llm_output)

            # Ensure raw_input is included
            parsed_json["raw_input"] = raw_input

            # Validate with Pydantic
            intent = ParsedTravelerIntent.model_validate(parsed_json)

            # Business rule validation
            self._validate_business_rules(intent)

            return intent

        except json.JSONDecodeError as e:
            logger.error(
                "LLM returned invalid JSON",
                extra={"error": str(e), "output_preview": llm_output[:200]},
            )

            # Attempt fallback parsing
            return await self._fallback_parse(llm_output, raw_input)

        except ValidationError as e:
            logger.warning(
                "Pydantic validation failed",
                extra={"errors": e.errors(), "output_preview": llm_output[:200]},
            )

            # Try fallback with relaxed validation
            return await self._fallback_parse(llm_output, raw_input)

    async def _fallback_parse(
        self,
        llm_output: str,
        raw_input: str,
    ) -> ParsedTravelerIntent:
        """
        Fallback parser for malformed LLM output.

        Extracts partial information and fills in sensible defaults.

        Args:
            llm_output: Potentially malformed JSON
            raw_input: Original input

        Returns:
            ParsedTravelerIntent with partial data and low confidence

        Raises:
            IntentParsingError: If even fallback fails
        """
        logger.info("Attempting fallback parsing")

        try:
            # Try to extract any valid JSON fragments
            partial_data = self._extract_partial_json(llm_output)

            # Build minimal valid intent
            fallback_intent = ParsedTravelerIntent(
                raw_input=raw_input,
                primary_destination=partial_data.get("destination", "Unknown"),
                destination_stays=[],  # Will be empty
                confidence_score=0.3,  # Low confidence for fallback
                ambiguities=partial_data.get("ambiguities", [
                    "Could not fully parse trip details",
                    "Please provide more specific information",
                ]),
                clarification_questions=[
                    "Where exactly are you traveling to?",
                    "What are your travel dates?",
                    "How long will you be traveling?",
                ],
            )

            logger.warning(
                "Fallback parsing succeeded with low confidence",
                extra={"confidence": fallback_intent.confidence_score},
            )

            return fallback_intent

        except Exception as e:
            logger.error(
                "Fallback parsing failed",
                extra={"error": str(e)},
            )
            raise IntentParsingError(
                "Could not parse travel intent even with fallback"
            ) from e

    def _extract_partial_json(self, text: str) -> dict[str, Any]:
        """
        Extract partial JSON data from malformed text.

        Uses heuristics to find JSON-like structures.

        Args:
            text: Potentially malformed JSON text

        Returns:
            Dict with extracted fields
        """
        partial = {}

        # Try to find destination
        if '"destination"' in text or '"primary_destination"' in text:
            # Simple regex-like extraction
            for line in text.split('\n'):
                if '"destination"' in line or '"primary_destination"' in line:
                    # Extract value between quotes after colon
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        value = parts[1].strip().strip('",')
                        if value:
                            partial["destination"] = value
                            break

        # Try to find ambiguities
        if '"ambiguities"' in text:
            partial["ambiguities"] = [
                "LLM output was malformed",
                "Could not extract complete trip details",
            ]

        return partial

    def _validate_business_rules(self, intent: ParsedTravelerIntent) -> None:
        """
        Validate business rules beyond schema validation.

        Args:
            intent: Parsed intent to validate

        Raises:
            ValidationError: If business rules are violated
        """
        # Check for unsupported destinations (basic filter)
        unsupported = ["North Korea", "Syria", "Yemen"]
        if intent.primary_destination in unsupported:
            logger.warning(
                "Unsupported destination detected",
                extra={"destination": intent.primary_destination},
            )
            # Don't block, but flag for review
            intent.ambiguities.append(
                f"Travel to {intent.primary_destination} may have restrictions"
            )

        # Check for contradictory preferences
        if intent.destination_stays:
            for stay in intent.destination_stays:
                # Can't have nightlife in very short stays
                if (
                    stay.nights == 1
                    and any("nightlife" in str(act).lower() for act in stay.activities)
                ):
                    logger.info("Flagging potential contradiction: nightlife in 1-night stay")
                    # Don't block, just note
                    intent.ambiguities.append(
                        "Very short stay with nightlife activities - verify timing"
                    )

        # Ensure confidence score reflects ambiguities
        if len(intent.ambiguities) > 3 and intent.confidence_score > 0.7:
            logger.info("Lowering confidence due to many ambiguities")
            intent.confidence_score = 0.6


class BatchIntentParser:
    """
    Batch processor for parsing multiple intents efficiently.

    Use for bulk operations, data migration, or testing.
    """

    def __init__(self, parser: IntentParser) -> None:
        self.parser = parser

    async def parse_batch(
        self,
        inputs: list[str],
        max_concurrent: int = 5,
    ) -> list[ParsedTravelerIntent | IntentParsingError]:
        """
        Parse multiple inputs with concurrency control.

        Args:
            inputs: List of raw input strings
            max_concurrent: Maximum concurrent LLM calls

        Returns:
            List of results (successful parses or errors)
        """
        import asyncio

        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)

        async def parse_with_semaphore(input_text: str) -> ParsedTravelerIntent | IntentParsingError:
            async with semaphore:
                try:
                    return await self.parser.parse(input_text)
                except Exception as e:
                    return IntentParsingError(str(e))

        # Process all inputs
        results = await asyncio.gather(
            *[parse_with_semaphore(inp) for inp in inputs],
            return_exceptions=True,
        )

        return results  # type: ignore


# Factory function for dependency injection
def get_intent_parser(prompt_version: str = "v2") -> IntentParser:
    """
    Get configured IntentParser instance.

    Args:
        prompt_version: Version of prompt to use

    Returns:
        Configured IntentParser
    """
    return IntentParser(prompt_version=prompt_version)
