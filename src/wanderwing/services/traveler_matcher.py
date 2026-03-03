"""
Traveler matching engine with layered architecture.

Architecture:
1. Deterministic Filters - Hard constraints (destination, dates, age, safety)
2. Semantic Scoring - Non-LLM compatibility calculation
3. Optional LLM Reranker - Generates explanations and adjusts ranking

This design prioritizes:
- Inspectability: Each layer is transparent and debuggable
- Testability: Pure functions with clear inputs/outputs
- Performance: Fast deterministic baseline, optional LLM enhancement
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional

from wanderwing.schemas.profile import AgeRange, TravelerProfile
from wanderwing.schemas.trip_enhanced import (
    ActivityCategory,
    BudgetTier,
    PacePreference,
    ParsedTravelerIntent,
)
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)


class SafetyFlag(str, Enum):
    """Safety-related flags for matches."""

    UNVERIFIED_PROFILE = "unverified_profile"
    LOW_TRUST_SCORE = "low_trust_score"
    AGE_MISMATCH = "age_mismatch"
    VISIBILITY_RESTRICTED = "visibility_restricted"
    NEW_USER = "new_user"


class MatchReason(str, Enum):
    """Reasons for matching travelers."""

    SAME_DESTINATION = "same_destination"
    OVERLAPPING_DATES = "overlapping_dates"
    SHARED_ACTIVITIES = "shared_activities"
    COMPATIBLE_BUDGET = "compatible_budget"
    SIMILAR_PACE = "similar_pace"
    COMPATIBLE_AGE = "compatible_age"
    COMPLEMENTARY_STYLES = "complementary_styles"
    SOCIAL_COMPATIBILITY = "social_compatibility"


@dataclass
class MatchScore:
    """Detailed match scoring breakdown."""

    overall_score: float  # 0.0-1.0

    # Component scores
    destination_score: float
    date_overlap_score: float
    activity_similarity: float
    budget_compatibility: float
    pace_compatibility: float
    social_compatibility: float
    age_compatibility: float

    # Match metadata
    top_reasons: list[MatchReason]
    confidence: float  # How confident we are in this match
    safety_flags: list[SafetyFlag]

    # LLM enhancement (optional)
    llm_rationale: Optional[str] = None
    llm_adjusted_score: Optional[float] = None


class DeterministicFilters:
    """Hard filters that must pass for any match."""

    @staticmethod
    def same_destination(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> bool:
        """Check if travelers are going to the same destination."""
        if not intent_a.primary_destination or not intent_b.primary_destination:
            return False
        return intent_a.primary_destination.lower() == intent_b.primary_destination.lower()

    @staticmethod
    def overlapping_dates(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
        min_overlap_days: int = 1,
    ) -> tuple[bool, int]:
        """
        Check if travel dates overlap.

        Returns:
            (has_overlap, overlap_days)
        """
        if not all([
            intent_a.overall_start_date,
            intent_a.overall_end_date,
            intent_b.overall_start_date,
            intent_b.overall_end_date,
        ]):
            # If dates missing, can't determine overlap
            return True, 0  # Allow match but flag confidence

        overlap_start = max(intent_a.overall_start_date, intent_b.overall_start_date)
        overlap_end = min(intent_a.overall_end_date, intent_b.overall_end_date)

        if overlap_start > overlap_end:
            return False, 0

        overlap_days = (overlap_end - overlap_start).days + 1
        return overlap_days >= min_overlap_days, overlap_days

    @staticmethod
    def age_compatible(
        profile_a: TravelerProfile,
        profile_b: TravelerProfile,
        strict: bool = False,
    ) -> bool:
        """
        Check age range compatibility.

        Args:
            strict: If True, age ranges must overlap. If False, allow one bracket difference.
        """
        if not profile_a.age_range or not profile_b.age_range:
            return True  # Unknown age, allow match but flag

        age_order = [
            AgeRange.UNDER_25,
            AgeRange.AGE_25_34,
            AgeRange.AGE_35_44,
            AgeRange.AGE_45_54,
            AgeRange.OVER_55,
        ]

        try:
            idx_a = age_order.index(profile_a.age_range)
            idx_b = age_order.index(profile_b.age_range)
            distance = abs(idx_a - idx_b)

            if strict:
                return distance == 0
            else:
                return distance <= 1  # Adjacent age brackets OK
        except ValueError:
            return True

    @staticmethod
    def safety_compatible(
        profile_a: TravelerProfile,
        profile_b: TravelerProfile,
    ) -> tuple[bool, list[SafetyFlag]]:
        """
        Check safety and visibility preferences.

        Returns:
            (is_compatible, safety_flags)
        """
        flags = []

        # Check verification levels
        if profile_a.verification_level == 0 or profile_b.verification_level == 0:
            flags.append(SafetyFlag.UNVERIFIED_PROFILE)

        # Check trust scores
        if profile_a.trust_score < 0.5 or profile_b.trust_score < 0.5:
            flags.append(SafetyFlag.LOW_TRUST_SCORE)

        # Check if profiles are new (created recently)
        if profile_a.created_at and (datetime.utcnow() - profile_a.created_at).days < 7:
            flags.append(SafetyFlag.NEW_USER)
        if profile_b.created_at and (datetime.utcnow() - profile_b.created_at).days < 7:
            flags.append(SafetyFlag.NEW_USER)

        # Check visibility preferences (if implemented)
        # For now, assume compatible unless specific restrictions

        # Allow match even with flags, but return them for user awareness
        return True, flags


class SemanticScorer:
    """Non-LLM semantic compatibility scoring."""

    @staticmethod
    def activity_similarity(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> tuple[float, list[ActivityCategory]]:
        """
        Calculate activity overlap using Jaccard similarity.

        Returns:
            (similarity_score, shared_activities)
        """
        activities_a = set(intent_a.activities) if intent_a.activities else set()
        activities_b = set(intent_b.activities) if intent_b.activities else set()

        if not activities_a or not activities_b:
            return 0.5, []  # Neutral if missing data

        intersection = activities_a & activities_b
        union = activities_a | activities_b

        similarity = len(intersection) / len(union) if union else 0.0
        return similarity, list(intersection)

    @staticmethod
    def budget_compatibility(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> float:
        """Calculate budget compatibility score."""
        if not intent_a.budget_tier or not intent_b.budget_tier:
            return 0.6  # Neutral if missing

        tier_order = [
            BudgetTier.SHOESTRING,
            BudgetTier.BUDGET,
            BudgetTier.MODERATE,
            BudgetTier.COMFORTABLE,
            BudgetTier.LUXURY,
        ]

        try:
            idx_a = tier_order.index(intent_a.budget_tier)
            idx_b = tier_order.index(intent_b.budget_tier)
            distance = abs(idx_a - idx_b)

            # Score decreases with distance
            # Same tier: 1.0, 1 apart: 0.75, 2 apart: 0.5, 3+: 0.25
            return max(0.25, 1.0 - (distance * 0.25))
        except ValueError:
            return 0.6

    @staticmethod
    def pace_compatibility(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> float:
        """Calculate travel pace compatibility."""
        if not intent_a.pace_preference or not intent_b.pace_preference:
            return 0.6  # Neutral

        if intent_a.pace_preference == intent_b.pace_preference:
            return 1.0

        # Different but workable
        pace_order = [PacePreference.RELAXED, PacePreference.MODERATE, PacePreference.FAST]

        try:
            idx_a = pace_order.index(intent_a.pace_preference)
            idx_b = pace_order.index(intent_b.pace_preference)
            distance = abs(idx_a - idx_b)

            # Adjacent paces are compatible
            return 0.8 if distance == 1 else 0.5
        except ValueError:
            return 0.6

    @staticmethod
    def social_compatibility(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> float:
        """Calculate social compatibility score."""
        # Both solo and open to companions
        if (intent_a.traveling_solo and intent_a.open_to_companions and
            intent_b.traveling_solo and intent_b.open_to_companions):
            return 1.0

        # Both solo but not explicitly open
        if intent_a.traveling_solo and intent_b.traveling_solo:
            return 0.7

        # Other combinations
        return 0.5

    @staticmethod
    def date_overlap_score(
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> float:
        """Calculate date overlap as proportion of total trip duration."""
        if not all([
            intent_a.overall_start_date,
            intent_a.overall_end_date,
            intent_b.overall_start_date,
            intent_b.overall_end_date,
        ]):
            return 0.5

        overlap_start = max(intent_a.overall_start_date, intent_b.overall_start_date)
        overlap_end = min(intent_a.overall_end_date, intent_b.overall_end_date)

        if overlap_start > overlap_end:
            return 0.0

        overlap_days = (overlap_end - overlap_start).days + 1
        max_duration = max(
            (intent_a.overall_end_date - intent_a.overall_start_date).days + 1,
            (intent_b.overall_end_date - intent_b.overall_start_date).days + 1,
        )

        return min(1.0, overlap_days / max_duration)

    @staticmethod
    def age_compatibility_score(
        profile_a: TravelerProfile,
        profile_b: TravelerProfile,
    ) -> float:
        """Calculate age compatibility score."""
        if not profile_a.age_range or not profile_b.age_range:
            return 0.6

        age_order = [
            AgeRange.UNDER_25,
            AgeRange.AGE_25_34,
            AgeRange.AGE_35_44,
            AgeRange.AGE_45_54,
            AgeRange.OVER_55,
        ]

        try:
            idx_a = age_order.index(profile_a.age_range)
            idx_b = age_order.index(profile_b.age_range)
            distance = abs(idx_a - idx_b)

            # Same bracket: 1.0, 1 apart: 0.8, 2 apart: 0.6, 3+: 0.4
            return max(0.4, 1.0 - (distance * 0.2))
        except ValueError:
            return 0.6


class TravelerMatcher:
    """
    Main matching engine with layered architecture.

    Layers:
    1. Deterministic filters (must pass)
    2. Semantic scoring (baseline)
    3. LLM reranking (optional)
    """

    def __init__(self, use_llm_reranker: bool = False):
        self.filters = DeterministicFilters()
        self.scorer = SemanticScorer()
        self.use_llm_reranker = use_llm_reranker

    def calculate_match(
        self,
        profile_a: TravelerProfile,
        intent_a: ParsedTravelerIntent,
        profile_b: TravelerProfile,
        intent_b: ParsedTravelerIntent,
        min_overlap_days: int = 1,
    ) -> Optional[MatchScore]:
        """
        Calculate match score between two travelers.

        Returns None if deterministic filters fail.
        """
        # Layer 1: Deterministic Filters
        if not self._passes_filters(
            profile_a, intent_a,
            profile_b, intent_b,
            min_overlap_days
        ):
            return None

        # Layer 2: Semantic Scoring
        match_score = self._calculate_semantic_score(
            profile_a, intent_a,
            profile_b, intent_b,
        )

        # Layer 3: Optional LLM Reranking
        if self.use_llm_reranker and match_score.overall_score >= 0.5:
            match_score = self._apply_llm_reranking(match_score, intent_a, intent_b)

        return match_score

    def _passes_filters(
        self,
        profile_a: TravelerProfile,
        intent_a: ParsedTravelerIntent,
        profile_b: TravelerProfile,
        intent_b: ParsedTravelerIntent,
        min_overlap_days: int,
    ) -> bool:
        """Apply deterministic filters."""
        # Destination must match
        if not self.filters.same_destination(intent_a, intent_b):
            logger.debug("Match rejected: different destinations")
            return False

        # Dates must overlap
        has_overlap, overlap_days = self.filters.overlapping_dates(
            intent_a, intent_b, min_overlap_days
        )
        if not has_overlap:
            logger.debug(f"Match rejected: insufficient date overlap ({overlap_days} days)")
            return False

        # Age must be compatible
        if not self.filters.age_compatible(profile_a, profile_b, strict=False):
            logger.debug("Match rejected: incompatible age ranges")
            return False

        # Safety checks (always pass, but collect flags)
        is_safe, flags = self.filters.safety_compatible(profile_a, profile_b)
        if not is_safe:
            logger.debug(f"Match rejected: safety flags {flags}")
            return False

        return True

    def _calculate_semantic_score(
        self,
        profile_a: TravelerProfile,
        intent_a: ParsedTravelerIntent,
        profile_b: TravelerProfile,
        intent_b: ParsedTravelerIntent,
    ) -> MatchScore:
        """Calculate non-LLM semantic compatibility score."""
        # Calculate component scores
        destination_score = 1.0  # Already filtered

        date_score = self.scorer.date_overlap_score(intent_a, intent_b)

        activity_sim, shared_activities = self.scorer.activity_similarity(intent_a, intent_b)

        budget_compat = self.scorer.budget_compatibility(intent_a, intent_b)

        pace_compat = self.scorer.pace_compatibility(intent_a, intent_b)

        social_compat = self.scorer.social_compatibility(intent_a, intent_b)

        age_compat = self.scorer.age_compatibility_score(profile_a, profile_b)

        # Weighted average (can be tuned)
        weights = {
            'destination': 0.20,
            'dates': 0.20,
            'activities': 0.20,
            'budget': 0.15,
            'pace': 0.10,
            'social': 0.10,
            'age': 0.05,
        }

        overall_score = (
            destination_score * weights['destination'] +
            date_score * weights['dates'] +
            activity_sim * weights['activities'] +
            budget_compat * weights['budget'] +
            pace_compat * weights['pace'] +
            social_compat * weights['social'] +
            age_compat * weights['age']
        )

        # Determine top reasons
        top_reasons = self._determine_reasons(
            destination_score, date_score, activity_sim,
            budget_compat, pace_compat, social_compat, age_compat
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            intent_a, intent_b, profile_a, profile_b
        )

        # Collect safety flags
        _, safety_flags = self.filters.safety_compatible(profile_a, profile_b)

        return MatchScore(
            overall_score=overall_score,
            destination_score=destination_score,
            date_overlap_score=date_score,
            activity_similarity=activity_sim,
            budget_compatibility=budget_compat,
            pace_compatibility=pace_compat,
            social_compatibility=social_compat,
            age_compatibility=age_compat,
            top_reasons=top_reasons,
            confidence=confidence,
            safety_flags=safety_flags,
        )

    def _determine_reasons(
        self,
        dest: float,
        dates: float,
        activities: float,
        budget: float,
        pace: float,
        social: float,
        age: float,
    ) -> list[MatchReason]:
        """Determine top reasons for match based on scores."""
        scores = [
            (dest, MatchReason.SAME_DESTINATION),
            (dates, MatchReason.OVERLAPPING_DATES),
            (activities, MatchReason.SHARED_ACTIVITIES),
            (budget, MatchReason.COMPATIBLE_BUDGET),
            (pace, MatchReason.SIMILAR_PACE),
            (age, MatchReason.COMPATIBLE_AGE),
            (social, MatchReason.SOCIAL_COMPATIBILITY),
        ]

        # Sort by score and take top reasons with score >= 0.7
        high_scores = [(score, reason) for score, reason in scores if score >= 0.7]
        high_scores.sort(reverse=True)

        return [reason for _, reason in high_scores[:5]]

    def _calculate_confidence(
        self,
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
        profile_a: TravelerProfile,
        profile_b: TravelerProfile,
    ) -> float:
        """Calculate confidence in this match."""
        confidence = 1.0

        # Reduce confidence for missing data
        if not intent_a.overall_start_date or not intent_b.overall_start_date:
            confidence -= 0.2

        if not intent_a.activities or not intent_b.activities:
            confidence -= 0.15

        if not intent_a.budget_tier or not intent_b.budget_tier:
            confidence -= 0.1

        if intent_a.confidence_score < 0.7 or intent_b.confidence_score < 0.7:
            confidence -= 0.2

        if profile_a.verification_level == 0 or profile_b.verification_level == 0:
            confidence -= 0.15

        return max(0.1, confidence)

    def _apply_llm_reranking(
        self,
        match_score: MatchScore,
        intent_a: ParsedTravelerIntent,
        intent_b: ParsedTravelerIntent,
    ) -> MatchScore:
        """Apply LLM reranking to generate rationale and adjust score."""
        # TODO: Implement LLM reranker
        # For now, return unchanged
        logger.debug("LLM reranking not yet implemented")
        return match_score


# Convenience function
def get_traveler_matcher(use_llm: bool = False) -> TravelerMatcher:
    """Get TravelerMatcher instance for dependency injection."""
    return TravelerMatcher(use_llm_reranker=use_llm)
