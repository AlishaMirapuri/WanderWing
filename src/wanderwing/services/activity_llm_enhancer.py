"""
LLM-based enhancement for activity recommendations.

Optional service that polishes explanations and meeting suggestions.
"""

import json
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from wanderwing.llm.client import get_llm_client
from wanderwing.schemas.activity import Activity, ActivityRecommendation
from wanderwing.schemas.trip_enhanced import ParsedTravelerIntent
from wanderwing.schemas.user import TravelerProfile
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class ActivityLLMEnhancer:
    """
    Optional LLM enhancement for activity recommendations.

    Design principles:
    - Non-blocking: Failures fall back to baseline explanations
    - Selective: Only enhances top recommendations to control cost
    - Transparent: Marks enhanced recommendations
    """

    def __init__(self):
        self.llm_client = get_llm_client()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        reraise=False,
    )
    async def enhance_recommendation(
        self,
        recommendation: ActivityRecommendation,
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> ActivityRecommendation:
        """
        Enhance a single recommendation with LLM.

        Args:
            recommendation: Baseline recommendation to enhance
            profiles: Traveler profiles
            intents: Travel intents

        Returns:
            Enhanced recommendation (or original if LLM fails)
        """
        try:
            prompt = self._build_prompt(
                recommendation.activity, profiles, intents, recommendation.shared_interests
            )

            response = await self.llm_client.complete(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
                response_format="json",
            )

            result = json.loads(response.content)

            # Update recommendation with LLM output
            recommendation.explanation = result.get(
                "explanation", recommendation.explanation
            )
            recommendation.meeting_suggestion = result.get(
                "meeting_suggestion", recommendation.meeting_suggestion
            )
            recommendation.llm_enhanced = True

            logger.info(
                "Enhanced recommendation with LLM",
                extra={
                    "activity": recommendation.activity.name,
                    "tokens": response.tokens_used,
                    "cost": response.cost_usd,
                },
            )

            return recommendation

        except json.JSONDecodeError as e:
            logger.warning(f"LLM enhancement failed (JSON parse): {e}")
            return recommendation

        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            return recommendation

    async def enhance_recommendations(
        self,
        recommendations: list[ActivityRecommendation],
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
        max_enhance: int = 3,
    ) -> list[ActivityRecommendation]:
        """
        Enhance multiple recommendations.

        Only enhances top N to control cost.

        Args:
            recommendations: List of recommendations
            profiles: Traveler profiles
            intents: Travel intents
            max_enhance: Maximum number to enhance (default 3)

        Returns:
            Enhanced recommendations
        """
        enhanced = []

        for i, rec in enumerate(recommendations):
            if i < max_enhance:
                enhanced_rec = await self.enhance_recommendation(rec, profiles, intents)
                enhanced.append(enhanced_rec)
            else:
                # Don't enhance beyond max_enhance
                enhanced.append(rec)

        return enhanced

    def _build_prompt(
        self,
        activity: Activity,
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
        shared_interests: list[str],
    ) -> str:
        """Build prompt for LLM enhancement."""
        traveler_count = len(profiles)

        # Summarize travelers
        traveler_summary = []
        for i, intent in enumerate(intents):
            activities = (
                ", ".join([str(a.value) for a in intent.activities[:3]])
                if intent.activities
                else "general sightseeing"
            )
            budget = intent.budget_tier.value if intent.budget_tier else "unspecified"
            pace = intent.pace_preference.value if intent.pace_preference else "moderate"
            traveler_summary.append(
                f"- Traveler {i+1}: Interested in {activities}. Budget: {budget}. Pace: {pace}."
            )

        travelers_str = "\n".join(traveler_summary)
        shared_str = ", ".join(shared_interests) if shared_interests else "various interests"

        prompt = f"""You are helping matched travelers plan shared activities.

## Activity
**{activity.name}**
{activity.description}

- Duration: {activity.duration_hours} hours
- Cost: {activity.cost_level.value}
- Tags: {", ".join([t.value for t in activity.tags])}
- Meeting-friendly: {activity.meeting_friendly}

## Travelers (Group of {traveler_count})
{travelers_str}

## Shared Interests
{shared_str}

## Your Task
Generate a warm, engaging recommendation for this activity. Your output should:

1. **Explanation** (2-3 sentences):
   - Why this activity is perfect for THIS specific group
   - Reference their shared interests naturally
   - Highlight what makes it a good first-time meetup (safe, fun, good for conversation)
   - Be specific, not generic

2. **Meeting Suggestion** (1-2 sentences):
   - Low-pressure, friendly invitation text
   - Natural and conversational
   - Mention practical details (time commitment, reservation needs)
   - Make it feel safe and optional

## Output Format (JSON only)
```json
{{
  "explanation": "Your 2-3 sentence explanation here",
  "meeting_suggestion": "Your 1-2 sentence meeting invitation here"
}}
```

## Examples

❌ Bad (generic):
"This is a great activity that you'll enjoy. It's fun and interesting."

✅ Good (specific):
"Given you both love food tours and want authentic experiences, this market walk is perfect. You'll get to taste local specialties while walking through less touristy neighborhoods, giving you plenty of time to chat and discover each other's favorite foods."

❌ Bad (too formal):
"I would like to formally invite you to participate in this activity with me."

✅ Good (casual, inviting):
"I'm planning to check this place out on Tuesday morning - want to join? It's about 2 hours and we can grab lunch nearby after."

Generate your JSON now.
"""

        return prompt


def get_activity_llm_enhancer() -> ActivityLLMEnhancer:
    """Get ActivityLLMEnhancer instance for dependency injection."""
    return ActivityLLMEnhancer()
