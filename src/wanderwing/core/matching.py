"""Matching engine - hybrid LLM + rule-based compatibility scoring."""

import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from wanderwing.db.repositories import TripRepository
from wanderwing.llm import get_llm_client
from wanderwing.schemas.match import MatchScore
from wanderwing.schemas.trip import ParsedItinerary
from wanderwing.utils.config import get_settings
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

PROMPTS_DIR = Path(__file__).parent.parent / "agents" / "prompts"


class MatchingEngine:
    """Engine for finding and scoring compatible travelers."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.trip_repo = TripRepository(db)

    async def find_matches_for_trip(
        self,
        trip_id: int,
        min_score: float = 0.5,
    ) -> list[tuple[int, MatchScore]]:
        """
        Find compatible trips for the given trip.

        Args:
            trip_id: Trip to find matches for
            min_score: Minimum compatibility score threshold

        Returns:
            List of (trip_id, MatchScore) tuples
        """
        trip = self.trip_repo.get_by_id(trip_id)
        if not trip or not trip.parsed_data:
            return []

        trip_data = ParsedItinerary.model_validate(trip.parsed_data)

        # Get all active trips except this one
        all_trips = self.trip_repo.list_active_trips(limit=1000)
        candidate_trips = [t for t in all_trips if t.id != trip_id and t.parsed_data]

        matches = []
        for candidate in candidate_trips:
            candidate_data = ParsedItinerary.model_validate(candidate.parsed_data)

            # Rule-based pre-filtering
            if not self._passes_basic_filters(trip_data, candidate_data):
                continue

            # Calculate hybrid score
            score = await calculate_match_score(trip_data, candidate_data)

            if score.overall_score >= min_score:
                matches.append((candidate.id, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1].overall_score, reverse=True)

        # Limit to max matches
        return matches[: settings.max_matches_per_trip]

    def _passes_basic_filters(
        self,
        trip_1: ParsedItinerary,
        trip_2: ParsedItinerary,
    ) -> bool:
        """Apply basic rule-based filters."""
        # Destination must match
        if trip_1.destination.lower() != trip_2.destination.lower():
            return False

        # Must have date overlap if dates are specified
        if trip_1.start_date and trip_1.end_date and trip_2.start_date and trip_2.end_date:
            if trip_1.end_date < trip_2.start_date or trip_2.end_date < trip_1.start_date:
                return False

        return True


async def calculate_match_score(
    trip_1: ParsedItinerary,
    trip_2: ParsedItinerary,
    use_llm: bool = True,
) -> MatchScore:
    """
    Calculate hybrid compatibility score between two trips.

    Args:
        trip_1: First trip itinerary
        trip_2: Second trip itinerary
        use_llm: Whether to use LLM for similarity scoring

    Returns:
        MatchScore with detailed breakdown
    """
    # Calculate rule-based components
    destination_overlap = _calculate_destination_overlap(trip_1, trip_2)
    date_overlap = _calculate_date_overlap(trip_1, trip_2)
    activity_similarity = _calculate_activity_similarity(trip_1, trip_2)
    budget_compatibility = _calculate_budget_compatibility(trip_1, trip_2)

    # Average rule-based score
    rule_based_score = (
        destination_overlap + date_overlap + activity_similarity + budget_compatibility
    ) / 4

    # LLM similarity (if enabled)
    llm_similarity = 0.5  # Default
    if use_llm:
        try:
            llm_similarity = await _calculate_llm_similarity(trip_1, trip_2)
        except Exception as e:
            logger.warning(f"LLM similarity calculation failed: {e}")

    # Hybrid score
    overall_score = (
        settings.llm_similarity_weight * llm_similarity
        + settings.rule_based_weight * rule_based_score
    )

    return MatchScore(
        overall_score=min(1.0, max(0.0, overall_score)),
        llm_similarity=llm_similarity,
        rule_based_score=rule_based_score,
        destination_overlap=destination_overlap,
        date_overlap=date_overlap,
        activity_similarity=activity_similarity,
        budget_compatibility=budget_compatibility,
    )


def _calculate_destination_overlap(trip_1: ParsedItinerary, trip_2: ParsedItinerary) -> float:
    """Calculate destination overlap score."""
    if trip_1.destination.lower() == trip_2.destination.lower():
        return 1.0
    return 0.0


def _calculate_date_overlap(trip_1: ParsedItinerary, trip_2: ParsedItinerary) -> float:
    """Calculate date overlap score."""
    if not (trip_1.start_date and trip_1.end_date and trip_2.start_date and trip_2.end_date):
        return 0.5  # Unknown, assume moderate compatibility

    # Calculate overlapping days
    overlap_start = max(trip_1.start_date, trip_2.start_date)
    overlap_end = min(trip_1.end_date, trip_2.end_date)

    if overlap_start > overlap_end:
        return 0.0

    overlap_days = (overlap_end - overlap_start).days + 1
    max_days = max(
        (trip_1.end_date - trip_1.start_date).days + 1,
        (trip_2.end_date - trip_2.start_date).days + 1,
    )

    return min(1.0, overlap_days / max_days)


def _calculate_activity_similarity(trip_1: ParsedItinerary, trip_2: ParsedItinerary) -> float:
    """Calculate activity similarity score."""
    if not trip_1.activities or not trip_2.activities:
        return 0.5

    activities_1 = set(trip_1.activities)
    activities_2 = set(trip_2.activities)

    intersection = len(activities_1 & activities_2)
    union = len(activities_1 | activities_2)

    if union == 0:
        return 0.0

    return intersection / union  # Jaccard similarity


def _calculate_budget_compatibility(trip_1: ParsedItinerary, trip_2: ParsedItinerary) -> float:
    """Calculate budget compatibility score."""
    budget_tiers = ["budget", "moderate", "comfortable", "luxury"]

    try:
        tier_1_idx = budget_tiers.index(trip_1.budget_tier.lower())
        tier_2_idx = budget_tiers.index(trip_2.budget_tier.lower())

        # Distance between budget tiers
        distance = abs(tier_1_idx - tier_2_idx)

        # Score: 1.0 for same tier, decreases with distance
        return max(0.0, 1.0 - (distance * 0.25))
    except ValueError:
        return 0.5


async def _calculate_llm_similarity(
    trip_1: ParsedItinerary,
    trip_2: ParsedItinerary,
) -> float:
    """Calculate LLM-based similarity score."""
    prompt_template = (PROMPTS_DIR / "matching_v1.txt").read_text()
    prompt = prompt_template.format(
        trip_1=trip_1.model_dump_json(indent=2),
        trip_2=trip_2.model_dump_json(indent=2),
    )

    llm_client = get_llm_client()
    response = await llm_client.complete_structured(
        prompt=prompt,
        temperature=0.1,
    )

    if isinstance(response, dict):
        return float(response.get("similarity_score", 0.5))

    return 0.5
