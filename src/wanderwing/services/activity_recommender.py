"""
Activity recommendation engine for matched travelers.

Recommends shared activities based on traveler profiles, intents, and local data.
"""

from typing import Optional

from wanderwing.data.activity_repository import ActivityRepository, get_activity_repository
from wanderwing.schemas.activity import (
    Activity,
    ActivityRecommendation,
    ActivityRecommendationResponse,
    ActivityTag,
    CostLevel,
    RecommendationReason,
)
from wanderwing.schemas.trip_enhanced import ParsedTravelerIntent
from wanderwing.schemas.user import TravelerProfile
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class ActivityRecommender:
    """
    Recommends shared activities for matched travelers.

    Architecture:
    1. Filter: Narrow candidate activities by hard constraints
    2. Score: Rank activities by compatibility
    3. Explain: Generate reasons and meeting suggestions (baseline)
    4. [Optional] LLM Enhance: Polish explanations with LLM

    Design principles:
    - Works without LLM (baseline explanations)
    - Scoring is transparent and debuggable
    - Prioritizes meeting-friendly, low-pressure activities
    """

    def __init__(self, repository: Optional[ActivityRepository] = None):
        """
        Initialize recommender.

        Args:
            repository: Activity data repository (injected for testing)
        """
        self.repository = repository or get_activity_repository()

    def recommend(
        self,
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
        limit: int = 5,
    ) -> ActivityRecommendationResponse:
        """
        Recommend activities for a group of matched travelers.

        Args:
            profiles: Traveler profiles (2+)
            intents: Parsed travel intents (same length as profiles)
            limit: Maximum recommendations to return (3-5)

        Returns:
            Structured recommendation response
        """
        if len(profiles) != len(intents):
            raise ValueError("Profiles and intents must have same length")

        if len(profiles) < 2:
            raise ValueError("Need at least 2 travelers for group recommendations")

        # Get destination from first intent (assume all matched travelers going to same place)
        destination = intents[0].primary_destination
        if not destination:
            raise ValueError("Destination must be specified")

        logger.info(
            f"Generating recommendations for {len(profiles)} travelers in {destination}"
        )

        # Load candidate activities
        candidates = self.repository.get_activities_for_city(destination)
        if not candidates:
            logger.warning(f"No activities found for {destination}")
            return ActivityRecommendationResponse(
                recommendations=[],
                destination=destination,
                traveler_count=len(profiles),
                fallback_mode=True,
            )

        # Filter activities
        filtered = self._filter_activities(candidates, profiles, intents)
        logger.debug(
            f"Filtered to {len(filtered)} activities from {len(candidates)} candidates"
        )

        # Score activities
        scored = self._score_activities(filtered, profiles, intents)

        # Sort by score and take top N
        scored.sort(key=lambda x: x[1], reverse=True)
        top_activities = scored[: min(limit, len(scored))]

        # Build recommendations with explanations
        recommendations = [
            self._build_recommendation(activity, score, profiles, intents)
            for activity, score in top_activities
        ]

        # Calculate date range
        date_range = self._get_date_range(intents)

        return ActivityRecommendationResponse(
            recommendations=recommendations,
            destination=destination,
            traveler_count=len(profiles),
            date_range=date_range,
            llm_used=False,
            fallback_mode=False,
        )

    def _filter_activities(
        self,
        candidates: list[Activity],
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> list[Activity]:
        """
        Filter activities by hard constraints.

        Filters:
        - Meeting-friendly only (public, safe)
        - Compatible with group size
        - Budget compatible (at least one person can afford)
        - Duration reasonable (not too long for first meetup)
        """
        filtered = candidates

        # Meeting-friendly only
        filtered = [a for a in filtered if a.meeting_friendly]

        # Group size compatible
        group_size = len(profiles)
        filtered = [
            a
            for a in filtered
            if a.group_size_min <= group_size <= a.group_size_max
        ]

        # Budget compatible (at least one person can afford)
        # Get maximum budget tier from group
        budget_tiers = [
            intent.budget_tier for intent in intents if intent.budget_tier
        ]
        if budget_tiers:
            max_budget = self._get_max_budget_tier(budget_tiers)
            filtered = self.repository.filter_activities(
                filtered, max_cost=max_budget
            )

        # Duration reasonable for meetup (exclude very long activities)
        filtered = [a for a in filtered if a.duration_hours <= 8.0]

        return filtered

    def _score_activities(
        self,
        activities: list[Activity],
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> list[tuple[Activity, float]]:
        """
        Score activities by compatibility.

        Scoring components:
        - Interest match: Do activities align with traveler interests?
        - Budget compatibility: Can all travelers afford it?
        - Introvert-friendliness: Lower pressure for introverts
        - Cultural depth: Bonus for authentic experiences
        - Popularity: Bonus for highly-rated activities

        Returns:
            List of (activity, score) tuples
        """
        scored = []

        for activity in activities:
            score = 0.0

            # Interest match (40% weight)
            interest_score = self._calculate_interest_match(activity, intents)
            score += interest_score * 0.40

            # Budget compatibility (20% weight)
            budget_score = self._calculate_budget_compatibility(activity, intents)
            score += budget_score * 0.20

            # Introvert-friendliness (15% weight)
            introvert_score = self._calculate_introvert_score(activity, profiles)
            score += introvert_score * 0.15

            # Cultural depth (10% weight)
            score += activity.cultural_depth * 0.10

            # Popularity (10% weight)
            if activity.typical_rating:
                popularity_score = activity.typical_rating / 5.0
                score += popularity_score * 0.10

            # Conversation-friendly bonus (5% weight)
            if activity.introvert_score >= 0.5:  # Good for conversation
                score += 0.05

            scored.append((activity, score))

        return scored

    def _calculate_interest_match(
        self, activity: Activity, intents: list[ParsedTravelerIntent]
    ) -> float:
        """
        Calculate how well activity matches traveler interests.

        Returns score 0.0-1.0 based on how many travelers' interests match.
        """
        if not activity.best_for:
            return 0.5  # Neutral if no categories specified

        total_match = 0.0
        for intent in intents:
            if not intent.activities:
                continue

            # Convert ActivityCategory enums to strings
            traveler_interests = [str(a.value).lower() for a in intent.activities]
            activity_categories = [bf.lower() for bf in activity.best_for]

            # Check overlap
            matches = any(
                interest in activity_categories
                or any(interest in cat for cat in activity_categories)
                for interest in traveler_interests
            )

            if matches:
                total_match += 1.0

        # Return percentage of travelers who match
        return total_match / len(intents)

    def _calculate_budget_compatibility(
        self, activity: Activity, intents: list[ParsedTravelerIntent]
    ) -> float:
        """
        Calculate budget compatibility.

        Returns 1.0 if all can afford, lower if some stretch their budget.
        """
        cost_order = ["free", "budget", "moderate", "expensive", "luxury"]
        activity_cost_index = cost_order.index(activity.cost_level.value)

        compatible_count = 0
        for intent in intents:
            if not intent.budget_tier:
                compatible_count += 1  # Assume compatible if unspecified
                continue

            traveler_budget_index = cost_order.index(intent.budget_tier.value)

            # Can afford if activity cost <= traveler budget
            if activity_cost_index <= traveler_budget_index:
                compatible_count += 1
            elif activity_cost_index == traveler_budget_index + 1:
                # One tier higher = stretch but doable
                compatible_count += 0.5

        return compatible_count / len(intents)

    def _calculate_introvert_score(
        self, activity: Activity, profiles: list[TravelerProfile]
    ) -> float:
        """
        Calculate introvert-friendliness.

        Higher score for lower-pressure activities when meeting new people.
        """
        # Activities with high introvert_score (0.6+) are good for first meetups
        # They allow conversation without overwhelming social pressure
        return activity.introvert_score

    def _build_recommendation(
        self,
        activity: Activity,
        score: float,
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> ActivityRecommendation:
        """
        Build recommendation with explanation and meeting suggestion.

        This is the baseline (non-LLM) explanation generator.
        """
        # Determine reasons
        reasons = self._determine_reasons(activity, profiles, intents)

        # Find shared interests
        shared_interests = self._find_shared_interests(activity, intents)

        # Generate explanation
        explanation = self._generate_baseline_explanation(
            activity, shared_interests, profiles, intents
        )

        # Generate meeting suggestion
        meeting_suggestion = self._generate_meeting_suggestion(
            activity, profiles, intents
        )

        # Estimate cost
        cost_estimate = self._estimate_cost(activity)

        return ActivityRecommendation(
            activity=activity,
            score=score,
            reasons=reasons,
            explanation=explanation,
            meeting_suggestion=meeting_suggestion,
            shared_interests=shared_interests,
            best_match_for=[p.user_id for p in profiles],
            estimated_cost_per_person=cost_estimate,
            llm_enhanced=False,
        )

    def _determine_reasons(
        self,
        activity: Activity,
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> list[RecommendationReason]:
        """Determine why this activity was recommended."""
        reasons = []

        # Check for shared interests
        shared_count = sum(
            1
            for intent in intents
            if intent.activities
            and any(
                str(a.value).lower() in [bf.lower() for bf in activity.best_for]
                for a in intent.activities
            )
        )

        if shared_count >= len(intents) / 2:
            reasons.append(RecommendationReason.SHARED_INTEREST)

        # Budget match
        if activity.cost_level in [CostLevel.FREE, CostLevel.BUDGET]:
            reasons.append(RecommendationReason.BUDGET_MATCH)

        # Introvert-friendly
        if activity.introvert_score >= 0.6:
            reasons.append(RecommendationReason.INTROVERT_FRIENDLY)
            reasons.append(RecommendationReason.LOW_PRESSURE)

        # Good for conversation
        if activity.introvert_score >= 0.5 and activity.duration_hours >= 1.5:
            reasons.append(RecommendationReason.GOOD_CONVERSATION)

        # Popular
        if activity.typical_rating and activity.typical_rating >= 4.7:
            reasons.append(RecommendationReason.POPULAR)

        return reasons[:5]  # Limit to top 5

    def _find_shared_interests(
        self, activity: Activity, intents: list[ParsedTravelerIntent]
    ) -> list[str]:
        """Find interests that all travelers share for this activity."""
        if not activity.best_for:
            return []

        shared = []
        for category in activity.best_for:
            match_count = sum(
                1
                for intent in intents
                if intent.activities
                and any(
                    str(a.value).lower() in category.lower()
                    or category.lower() in str(a.value).lower()
                    for a in intent.activities
                )
            )

            if match_count >= len(intents) / 2:  # At least half
                shared.append(category.replace("_", " ").title())

        return shared

    def _generate_baseline_explanation(
        self,
        activity: Activity,
        shared_interests: list[str],
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> str:
        """
        Generate baseline (non-LLM) explanation.

        Template-based explanation that's functional but not as polished as LLM.
        """
        parts = []

        # Start with activity description
        parts.append(activity.description)

        # Add shared interest context
        if shared_interests:
            interests_str = ", ".join(shared_interests[:2])
            parts.append(f"Great match for your shared interest in {interests_str}.")

        # Add practical details
        if activity.cost_level in [CostLevel.FREE, CostLevel.BUDGET]:
            parts.append("Budget-friendly option.")

        if activity.introvert_score >= 0.6:
            parts.append("Low-pressure atmosphere, perfect for getting to know each other.")

        if activity.typical_rating and activity.typical_rating >= 4.7:
            parts.append(f"Highly rated ({activity.typical_rating}/5.0) by visitors.")

        return " ".join(parts)

    def _generate_meeting_suggestion(
        self,
        activity: Activity,
        profiles: list[TravelerProfile],
        intents: list[ParsedTravelerIntent],
    ) -> str:
        """
        Generate safe, low-pressure meeting invitation text.

        Design: Use neutral, inviting language that feels safe and casual.
        """
        activity_name = activity.name
        duration = activity.duration_hours

        # Template variations based on activity type
        if ActivityTag.FOOD in activity.tags:
            templates = [
                f"Would you be interested in trying {activity_name} together? I've heard great things about it.",
                f"I'm planning to check out {activity_name} - want to join?",
            ]
        elif ActivityTag.OUTDOORS in activity.tags or ActivityTag.ADVENTURE in activity.tags:
            templates = [
                f"Looking for a {activity_name.lower()} buddy! Interested in joining?",
                f"Planning to do {activity_name} - would love some company if you're interested.",
            ]
        elif ActivityTag.CULTURE in activity.tags:
            templates = [
                f"I'm thinking of visiting {activity_name}. Want to explore together?",
                f"Would you like to check out {activity_name} together during your trip?",
            ]
        else:
            templates = [
                f"Interested in doing {activity_name} together?",
                f"I'm planning to visit {activity_name} - feel free to join if you'd like!",
            ]

        # Pick first template (in real system, could randomize)
        suggestion = templates[0]

        # Add time commitment if significant
        if duration >= 3.0:
            suggestion += f" It takes about {int(duration)} hours."

        # Add reservation note if needed
        if activity.reservation_required:
            suggestion += " We'd need to book in advance."

        return suggestion

    def _estimate_cost(self, activity: Activity) -> Optional[str]:
        """Estimate cost per person."""
        cost_map = {
            CostLevel.FREE: "Free",
            CostLevel.BUDGET: "$5-20",
            CostLevel.MODERATE: "$20-50",
            CostLevel.EXPENSIVE: "$50-100",
            CostLevel.LUXURY: "$100+",
        }
        return cost_map.get(activity.cost_level)

    def _get_max_budget_tier(self, budget_tiers: list) -> CostLevel:
        """Get maximum budget tier from list."""
        cost_order = {
            "budget": 1,
            "moderate": 2,
            "comfortable": 3,
            "luxury": 4,
        }

        max_tier = "budget"
        max_value = 0

        for tier in budget_tiers:
            tier_str = tier.value if hasattr(tier, "value") else str(tier)
            tier_value = cost_order.get(tier_str.lower(), 0)
            if tier_value > max_value:
                max_value = tier_value
                max_tier = tier_str

        # Map to CostLevel
        mapping = {
            "budget": CostLevel.BUDGET,
            "moderate": CostLevel.MODERATE,
            "comfortable": CostLevel.EXPENSIVE,
            "luxury": CostLevel.LUXURY,
        }

        return mapping.get(max_tier.lower(), CostLevel.MODERATE)

    def _get_date_range(self, intents: list[ParsedTravelerIntent]) -> Optional[str]:
        """Get overlapping date range."""
        dates = [
            (intent.overall_start_date, intent.overall_end_date)
            for intent in intents
            if intent.overall_start_date and intent.overall_end_date
        ]

        if not dates:
            return None

        # Find overlap
        overlap_start = max(d[0] for d in dates)
        overlap_end = min(d[1] for d in dates)

        if overlap_start <= overlap_end:
            return f"{overlap_start.strftime('%b %d')} - {overlap_end.strftime('%b %d, %Y')}"

        return None


def get_activity_recommender() -> ActivityRecommender:
    """Get ActivityRecommender instance for dependency injection."""
    return ActivityRecommender()
