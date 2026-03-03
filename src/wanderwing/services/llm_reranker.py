"""
LLM-based match reranking and explanation generation.

This module provides optional LLM enhancement for match scoring:
- Generates human-readable rationales
- Can adjust scores based on nuanced factors
- Provides conversation starters

Kept separate from core matching for:
- Cost control (optional enhancement)
- Performance (async/batch processing)
- Testing (can be mocked/disabled)
"""

import json
from pathlib import Path
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from wanderwing.llm.client import get_llm_client
from wanderwing.schemas.trip_enhanced import ParsedTravelerIntent
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "agents" / "prompts"


class LLMMatchReranker:
    """
    Optional LLM-based match reranking and explanation.

    Design principles:
    - Non-blocking: Failures don't break matching
    - Cost-aware: Only called for promising matches (score >= 0.5)
    - Transparent: Returns rationale for adjustments
    """

    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load prompt template for match reranking."""
        prompt_path = PROMPTS_DIR / "match_reranking_v1.txt"
        if prompt_path.exists():
            return prompt_path.read_text()

        # Fallback inline prompt
        return """You are a travel companion matching expert.

Analyze these two travelers and provide a compatibility assessment.

Traveler A:
{traveler_a}

Traveler B:
{traveler_b}

Current compatibility scores:
- Activity similarity: {activity_score:.2f}
- Budget compatibility: {budget_score:.2f}
- Pace compatibility: {pace_score:.2f}
- Overall score: {overall_score:.2f}

Generate a JSON response:
{{
  "adjusted_score": 0.0-1.0,
  "rationale": "2-3 sentence explanation of compatibility",
  "key_strengths": ["strength 1", "strength 2", "strength 3"],
  "potential_concerns": ["concern 1" (optional)],
  "conversation_starters": ["starter 1", "starter 2"]
}}

Rules:
- adjusted_score should be within ±0.15 of overall_score
- Be specific and concrete
- Focus on unique compatibility factors not captured by simple scoring
- JSON only, no additional text
"""

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        reraise=False,
    )
    async def rerank(
        self,
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
        current_score: float,
        activity_score: float,
        budget_score: float,
        pace_score: float,
    ) -> tuple[Optional[float], Optional[str], dict[str, Any]]:
        """
        Generate LLM-based reranking and rationale.

        Returns:
            (adjusted_score, rationale, metadata)
        """
        try:
            # Build prompt
            prompt = self.prompt_template.format(
                traveler_a=self._format_intent(intent_a),
                traveler_b=self._format_intent(intent_b),
                activity_score=activity_score,
                budget_score=budget_score,
                pace_score=pace_score,
                overall_score=current_score,
            )

            # Call LLM
            response = await self.llm_client.complete(
                prompt=prompt,
                temperature=0.3,
                max_tokens=800,
                response_format="json",
            )

            # Parse response
            result = json.loads(response.content)

            adjusted_score = float(result.get("adjusted_score", current_score))
            rationale = result.get("rationale", "")

            metadata = {
                "key_strengths": result.get("key_strengths", []),
                "potential_concerns": result.get("potential_concerns", []),
                "conversation_starters": result.get("conversation_starters", []),
                "tokens_used": response.tokens_used,
                "cost_usd": response.cost_usd,
            }

            logger.info(
                "LLM reranking completed",
                extra={
                    "original_score": current_score,
                    "adjusted_score": adjusted_score,
                    "tokens": response.tokens_used,
                    "cost": response.cost_usd,
                },
            )

            return adjusted_score, rationale, metadata

        except json.JSONDecodeError as e:
            logger.warning(f"LLM reranking failed (JSON parse): {e}")
            return None, None, {}

        except Exception as e:
            logger.error(f"LLM reranking failed: {e}")
            return None, None, {}

    def _format_intent(self, intent: ParsedTravelerIntent) -> str:
        """Format intent for LLM prompt (compact JSON)."""
        data = {
            "destination": intent.primary_destination,
            "dates": f"{intent.overall_start_date} to {intent.overall_end_date}" if intent.overall_start_date else "unspecified",
            "duration_days": (intent.overall_end_date - intent.overall_start_date).days + 1 if intent.overall_start_date and intent.overall_end_date else "unknown",
            "activities": [str(a.value) if hasattr(a, 'value') else str(a) for a in (intent.activities or [])[:5]],
            "budget": intent.budget_tier.value if intent.budget_tier else "unspecified",
            "pace": intent.pace_preference.value if intent.pace_preference else "unspecified",
            "solo": intent.traveling_solo,
            "open_to_companions": intent.open_to_companions,
        }
        return json.dumps(data, indent=2)


def get_llm_reranker() -> LLMMatchReranker:
    """Get LLMMatchReranker instance for dependency injection."""
    return LLMMatchReranker()
