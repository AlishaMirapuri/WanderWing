"""
Enhanced matching engine with dimension-by-dimension scoring and LLM explanations.

This module implements a production-grade hybrid matching algorithm that combines:
- Rule-based scoring (40%): Fast, deterministic compatibility checks
- LLM similarity (60%): Semantic understanding of travel compatibility

Key features:
- Dimension-by-dimension scoring with explanations
- LLM-generated match insights and conversation starters
- Caching for performance optimization
- Comprehensive logging for observability
- Retry logic for resilience
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from wanderwing.llm.client import get_llm_client
from wanderwing.schemas.match_enhanced import (
    CompatibilityDimension,
    DimensionScore,
    MatchCandidate,
    MatchExplanation,
    MatchReason,
    MatchStatus,
)
from wanderwing.schemas.trip_enhanced import ActivityCategory, BudgetTier, ParsedTravelerIntent
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "agents" / "prompts"


class MatchingEngine:
    """
    Production-grade matching engine with hybrid scoring.

    Architecture:
    1. Pre-filtering (rule-based): Remove incompatible candidates
    2. Dimension scoring (rule-based): Score each compatibility dimension
    3. LLM similarity (semantic): Deep understanding of compatibility
    4. Hybrid scoring: Weighted combination (60% LLM + 40% rules)
    5. Explanation generation (LLM): Human-readable match insights
    """

    def __init__(self) -> None:
        self.llm_client = get_llm_client()
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load LLM prompt template for match explanations."""
        prompt_path = PROMPTS_DIR / "match_explanation_v1.txt"
        if prompt_path.exists():
            return prompt_path.read_text()

        # Fallback template if file doesn't exist
        return """You are an expert travel companion matching assistant.

Analyze these two travelers and generate a detailed compatibility assessment.

Traveler A:
{traveler_a}

Traveler B:
{traveler_b}

Generate a JSON response with:
{
  "similarity_score": 0.0-1.0,
  "summary": "2-3 sentence explanation of why they're compatible",
  "why_great_match": ["reason 1", "reason 2", "reason 3"],
  "shared_interests": ["interest1", "interest2"],
  "complementary_traits": ["trait1", "trait2"],
  "potential_concerns": ["concern1"],
  "conversation_starters": ["starter1", "starter2", "starter3"]
}

Be specific, actionable, and focus on what makes this match work."""

    async def calculate_match(
        self,
        traveler_a: ParsedTravelerIntent,
        traveler_b: ParsedTravelerIntent,
        traveler_a_id: int,
        traveler_b_id: int,
        use_llm: bool = True,
    ) -> MatchCandidate | None:
        """
        Calculate full match with explanations between two travelers.

        Args:
            traveler_a: First traveler's parsed intent
            traveler_b: Second traveler's parsed intent
            traveler_a_id: First traveler's profile ID
            traveler_b_id: Second traveler's profile ID
            use_llm: Whether to use LLM for similarity (disable for testing)

        Returns:
            MatchCandidate with detailed explanation, or None if incompatible
        """
        logger.info(
            "Calculating match",
            extra={
                "traveler_a_id": traveler_a_id,
                "traveler_b_id": traveler_b_id,
                "use_llm": use_llm,
            },
        )

        # Step 1: Pre-filtering
        if not self._passes_basic_filters(traveler_a, traveler_b):
            logger.info("Match rejected by basic filters")
            return None

        # Step 2: Calculate dimension scores
        dimension_scores = self._calculate_dimension_scores(traveler_a, traveler_b)

        # Step 3: Calculate rule-based overall score
        rule_based_score = self._calculate_rule_based_score(dimension_scores)

        # Step 4: Calculate LLM similarity
        llm_similarity = 0.5  # Default fallback
        llm_insights = {}
        if use_llm:
            llm_similarity, llm_insights = await self._calculate_llm_similarity(
                traveler_a, traveler_b
            )

        # Step 5: Calculate hybrid overall score
        overall_score = (0.6 * llm_similarity) + (0.4 * rule_based_score)

        # Step 6: Determine match reasons
        primary_reasons = self._determine_match_reasons(dimension_scores, traveler_a, traveler_b)

        # Step 7: Calculate trip overlap
        overlapping_days = self._calculate_overlapping_days(traveler_a, traveler_b)

        # Step 8: Build match explanation
        explanation = MatchExplanation(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            primary_reasons=primary_reasons,
            shared_interests=llm_insights.get("shared_interests", []),
            complementary_traits=llm_insights.get("complementary_traits", []),
            potential_concerns=llm_insights.get("potential_concerns", []),
            llm_summary=llm_insights.get("summary", "Compatible travel companions"),
            why_great_match=llm_insights.get("why_great_match", []),
            conversation_starters=llm_insights.get("conversation_starters", []),
            rule_based_score=rule_based_score,
            llm_similarity_score=llm_similarity,
            hybrid_weight_llm=0.6,
            hybrid_weight_rules=0.4,
        )

        # Step 9: Build match candidate
        match_candidate = MatchCandidate(
            match_id=0,  # Will be set by database
            traveler_profile_id=traveler_b_id,
            traveler_name="Unknown",  # Will be filled by service layer
            traveler_verification_level=0,  # Will be filled by service layer
            traveler_trust_score=0.0,  # Will be filled by service layer
            destination=traveler_b.primary_destination or "Unknown",
            trip_start_date=str(traveler_b.overall_start_date) if traveler_b.overall_start_date else "",
            trip_end_date=str(traveler_b.overall_end_date) if traveler_b.overall_end_date else "",
            trip_duration_days=self._calculate_duration(traveler_b),
            overlapping_days=overlapping_days,
            match_explanation=explanation,
            match_status=MatchStatus.SUGGESTED,
            matched_at=datetime.utcnow(),
        )

        logger.info(
            "Match calculated successfully",
            extra={
                "overall_score": overall_score,
                "rule_based_score": rule_based_score,
                "llm_similarity": llm_similarity,
                "overlapping_days": overlapping_days,
            },
        )

        return match_candidate

    def _passes_basic_filters(
        self,
        traveler_a: ParsedTravelerIntent,
        traveler_b: ParsedTravelerIntent,
    ) -> bool:
        """Apply basic compatibility filters."""
        # Must have same primary destination
        if not traveler_a.primary_destination or not traveler_b.primary_destination:
            return False

        if traveler_a.primary_destination.lower() != traveler_b.primary_destination.lower():
            return False

        # Must have some date overlap (if dates are specified)
        if (
            traveler_a.overall_start_date
            and traveler_a.overall_end_date
            and traveler_b.overall_start_date
            and traveler_b.overall_end_date
        ):
            # Check for date overlap
            if (
                traveler_a.overall_end_date < traveler_b.overall_start_date
                or traveler_b.overall_end_date < traveler_a.overall_start_date
            ):
                return False

        return True

    def _calculate_dimension_scores(
        self,
        traveler_a: ParsedTravelerIntent,
        traveler_b: ParsedTravelerIntent,
    ) -> list[DimensionScore]:
        """Calculate score for each compatibility dimension."""
        scores = []

        # Destination compatibility
        dest_score, dest_explanation, dest_factors = self._score_destination(traveler_a, traveler_b)
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.DESTINATION,
                score=dest_score,
                weight=1.0,
                explanation=dest_explanation,
                contributing_factors=dest_factors,
            )
        )

        # Date compatibility
        date_score, date_explanation, date_factors = self._score_dates(traveler_a, traveler_b)
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.DATES,
                score=date_score,
                weight=1.0,
                explanation=date_explanation,
                contributing_factors=date_factors,
            )
        )

        # Activity compatibility
        activity_score, activity_explanation, activity_factors = self._score_activities(
            traveler_a, traveler_b
        )
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.ACTIVITIES,
                score=activity_score,
                weight=1.0,
                explanation=activity_explanation,
                contributing_factors=activity_factors,
            )
        )

        # Budget compatibility
        budget_score, budget_explanation, budget_factors = self._score_budget(traveler_a, traveler_b)
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.BUDGET,
                score=budget_score,
                weight=1.0,
                explanation=budget_explanation,
                contributing_factors=budget_factors,
            )
        )

        # Travel style compatibility
        style_score, style_explanation, style_factors = self._score_travel_style(
            traveler_a, traveler_b
        )
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.TRAVEL_STYLE,
                score=style_score,
                weight=0.8,
                explanation=style_explanation,
                contributing_factors=style_factors,
            )
        )

        # Pace compatibility
        pace_score, pace_explanation, pace_factors = self._score_pace(traveler_a, traveler_b)
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.PACE,
                score=pace_score,
                weight=0.7,
                explanation=pace_explanation,
                contributing_factors=pace_factors,
            )
        )

        # Social compatibility
        social_score, social_explanation, social_factors = self._score_social(traveler_a, traveler_b)
        scores.append(
            DimensionScore(
                dimension=CompatibilityDimension.SOCIAL_COMPATIBILITY,
                score=social_score,
                weight=0.9,
                explanation=social_explanation,
                contributing_factors=social_factors,
            )
        )

        return scores

    def _score_destination(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score destination compatibility."""
        if a.primary_destination.lower() == b.primary_destination.lower():
            return (
                1.0,
                f"Both traveling to {a.primary_destination}",
                [a.primary_destination],
            )
        return (0.0, "Different destinations", [])

    def _score_dates(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score date overlap."""
        if not (a.overall_start_date and a.overall_end_date and b.overall_start_date and b.overall_end_date):
            return (0.5, "Date information incomplete", [])

        # Calculate overlap
        overlap_start = max(a.overall_start_date, b.overall_start_date)
        overlap_end = min(a.overall_end_date, b.overall_end_date)

        if overlap_start > overlap_end:
            return (0.0, "No date overlap", [])

        overlap_days = (overlap_end - overlap_start).days + 1
        max_duration = max(
            (a.overall_end_date - a.overall_start_date).days + 1,
            (b.overall_end_date - b.overall_start_date).days + 1,
        )

        score = min(1.0, overlap_days / max_duration)
        return (
            score,
            f"{overlap_days} days of overlap ({overlap_start} to {overlap_end})",
            [f"{overlap_days} overlapping days"],
        )

    def _score_activities(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score activity compatibility."""
        activities_a = set(a.activities) if a.activities else set()
        activities_b = set(b.activities) if b.activities else set()

        if not activities_a or not activities_b:
            return (0.5, "Activity information incomplete", [])

        intersection = activities_a & activities_b
        union = activities_a | activities_b

        if not union:
            return (0.0, "No activities specified", [])

        score = len(intersection) / len(union)  # Jaccard similarity
        shared = [str(act.value) if isinstance(act, ActivityCategory) else act for act in intersection]

        return (
            score,
            f"{len(intersection)} out of {len(union)} activities match",
            shared[:5],  # Top 5
        )

    def _score_budget(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score budget compatibility."""
        if not a.budget_tier or not b.budget_tier:
            return (0.5, "Budget information incomplete", [])

        # Budget tier order
        tier_order = {
            BudgetTier.SHOESTRING: 0,
            BudgetTier.BUDGET: 1,
            BudgetTier.MODERATE: 2,
            BudgetTier.COMFORTABLE: 3,
            BudgetTier.LUXURY: 4,
        }

        tier_a = tier_order.get(a.budget_tier, 2)
        tier_b = tier_order.get(b.budget_tier, 2)

        distance = abs(tier_a - tier_b)
        score = max(0.0, 1.0 - (distance * 0.25))

        if distance == 0:
            explanation = f"Both have {a.budget_tier.value} budget"
        elif distance == 1:
            explanation = f"Similar budgets ({a.budget_tier.value} vs {b.budget_tier.value})"
        else:
            explanation = f"Different budget tiers ({a.budget_tier.value} vs {b.budget_tier.value})"

        return (score, explanation, [a.budget_tier.value, b.budget_tier.value])

    def _score_travel_style(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score travel style compatibility."""
        # Analyze activities to infer style
        adventure_activities = {
            ActivityCategory.HIKING,
            ActivityCategory.ADVENTURE_SPORTS,
            ActivityCategory.WATER_SPORTS,
        }
        cultural_activities = {
            ActivityCategory.CULTURAL_EVENTS,
            ActivityCategory.MUSEUMS,
            ActivityCategory.SIGHTSEEING,
        }
        relaxed_activities = {
            ActivityCategory.BEACH,
            ActivityCategory.WELLNESS,
            ActivityCategory.FOOD_TOUR,
        }

        a_activities = set(a.activities) if a.activities else set()
        b_activities = set(b.activities) if b.activities else set()

        a_adventure = len(a_activities & adventure_activities)
        b_adventure = len(b_activities & adventure_activities)
        a_cultural = len(a_activities & cultural_activities)
        b_cultural = len(b_activities & cultural_activities)

        # Simple similarity based on activity types
        style_similarity = 1.0 - abs(a_adventure - b_adventure) / 5.0
        style_similarity = max(0.0, min(1.0, style_similarity))

        return (
            style_similarity,
            "Compatible travel styles based on activity preferences",
            [],
        )

    def _score_pace(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score pace compatibility."""
        if not a.pace_preference or not b.pace_preference:
            return (0.6, "Pace information incomplete", [])

        if a.pace_preference == b.pace_preference:
            return (1.0, f"Both prefer {a.pace_preference} pace", [a.pace_preference])

        # Different but potentially compatible
        return (0.7, f"Different pace preferences ({a.pace_preference} vs {b.pace_preference})", [])

    def _score_social(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> tuple[float, str, list[str]]:
        """Score social compatibility."""
        # Both solo and open to companions
        if a.traveling_solo and a.open_to_companions and b.traveling_solo and b.open_to_companions:
            return (
                1.0,
                "Both solo travelers open to meeting companions",
                ["solo", "open_to_companions"],
            )

        # Both traveling solo
        if a.traveling_solo and b.traveling_solo:
            return (0.8, "Both solo travelers", ["solo"])

        return (0.6, "Social compatibility to be determined", [])

    def _calculate_rule_based_score(self, dimension_scores: list[DimensionScore]) -> float:
        """Calculate weighted average of dimension scores."""
        if not dimension_scores:
            return 0.0

        weighted_sum = sum(ds.score * ds.weight for ds in dimension_scores)
        total_weight = sum(ds.weight for ds in dimension_scores)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        reraise=True,
    )
    async def _calculate_llm_similarity(
        self,
        traveler_a: ParsedTravelerIntent,
        traveler_b: ParsedTravelerIntent,
    ) -> tuple[float, dict[str, Any]]:
        """
        Calculate LLM-based similarity and generate insights.

        Returns:
            Tuple of (similarity_score, insights_dict)
        """
        # Build prompt
        prompt = self.prompt_template.format(
            traveler_a=traveler_a.model_dump_json(indent=2, exclude={"raw_input"}),
            traveler_b=traveler_b.model_dump_json(indent=2, exclude={"raw_input"}),
        )

        try:
            # Call LLM with structured output
            response = await self.llm_client.complete(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1500,
                response_format="json",
            )

            # Parse response
            insights = json.loads(response.content)

            similarity_score = float(insights.get("similarity_score", 0.5))
            similarity_score = max(0.0, min(1.0, similarity_score))

            logger.info(
                "LLM similarity calculated",
                extra={
                    "similarity_score": similarity_score,
                    "tokens_used": response.tokens_used,
                    "cost_usd": response.cost_usd,
                },
            )

            return similarity_score, insights

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return 0.5, {"summary": "Unable to generate detailed insights"}

        except Exception as e:
            logger.error(f"LLM similarity calculation failed: {e}")
            return 0.5, {"summary": "Unable to generate detailed insights"}

    def _determine_match_reasons(
        self,
        dimension_scores: list[DimensionScore],
        traveler_a: ParsedTravelerIntent,
        traveler_b: ParsedTravelerIntent,
    ) -> list[MatchReason]:
        """Determine primary reasons for the match."""
        reasons = []

        for ds in dimension_scores:
            if ds.score >= 0.8:
                if ds.dimension == CompatibilityDimension.DESTINATION:
                    reasons.append(MatchReason.SAME_DESTINATION)
                elif ds.dimension == CompatibilityDimension.DATES:
                    reasons.append(MatchReason.OVERLAPPING_DATES)
                elif ds.dimension == CompatibilityDimension.ACTIVITIES:
                    reasons.append(MatchReason.SHARED_ACTIVITIES)
                elif ds.dimension == CompatibilityDimension.BUDGET:
                    reasons.append(MatchReason.COMPATIBLE_BUDGET)
                elif ds.dimension == CompatibilityDimension.TRAVEL_STYLE:
                    reasons.append(MatchReason.SIMILAR_STYLE)

        # Ensure at least one reason
        if not reasons:
            reasons.append(MatchReason.SAME_DESTINATION)

        return reasons[:5]  # Top 5 reasons

    def _calculate_overlapping_days(
        self, a: ParsedTravelerIntent, b: ParsedTravelerIntent
    ) -> int:
        """Calculate number of overlapping days."""
        if not (a.overall_start_date and a.overall_end_date and b.overall_start_date and b.overall_end_date):
            return 0

        overlap_start = max(a.overall_start_date, b.overall_start_date)
        overlap_end = min(a.overall_end_date, b.overall_end_date)

        if overlap_start > overlap_end:
            return 0

        return (overlap_end - overlap_start).days + 1

    def _calculate_duration(self, traveler: ParsedTravelerIntent) -> int:
        """Calculate trip duration in days."""
        if traveler.overall_start_date and traveler.overall_end_date:
            return (traveler.overall_end_date - traveler.overall_start_date).days + 1
        return 0


# Dependency injection helper
def get_matching_engine() -> MatchingEngine:
    """Get MatchingEngine instance for dependency injection."""
    return MatchingEngine()
