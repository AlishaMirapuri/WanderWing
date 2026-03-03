"""
Activity data repository.

Handles loading and querying activity data from local JSON files.
"""

import json
from pathlib import Path
from typing import Optional

from wanderwing.schemas.activity import Activity, ActivityTag, CostLevel
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).parent / "activities"


class ActivityRepository:
    """
    Repository for loading and querying activities.

    Design:
    - Loads data lazily (only when requested)
    - Caches loaded data in memory
    - Provides filtering by city, tags, cost, etc.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize repository.

        Args:
            data_dir: Override default data directory (useful for testing)
        """
        self.data_dir = data_dir or DATA_DIR
        self._cache: dict[str, list[Activity]] = {}

    def get_activities_for_city(self, city: str) -> list[Activity]:
        """
        Get all activities for a city.

        Args:
            city: City name (case-insensitive)

        Returns:
            List of activities, empty if city not found
        """
        city_normalized = city.lower().strip()

        # Check cache
        if city_normalized in self._cache:
            return self._cache[city_normalized]

        # Load from file
        city_file = self.data_dir / f"{city_normalized}.json"
        if not city_file.exists():
            logger.warning(f"No activity data found for city: {city}")
            return []

        try:
            with open(city_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            activities = [Activity(**activity) for activity in data["activities"]]
            self._cache[city_normalized] = activities

            logger.info(
                f"Loaded {len(activities)} activities for {city}",
                extra={"city": city, "count": len(activities)},
            )

            return activities

        except Exception as e:
            logger.error(f"Failed to load activities for {city}: {e}")
            return []

    def filter_activities(
        self,
        activities: list[Activity],
        tags: Optional[list[ActivityTag]] = None,
        max_cost: Optional[CostLevel] = None,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        meeting_friendly_only: bool = False,
        best_for: Optional[list[str]] = None,
    ) -> list[Activity]:
        """
        Filter activities by criteria.

        Args:
            activities: Activities to filter
            tags: Must have at least one of these tags
            max_cost: Maximum cost level
            min_duration: Minimum duration in hours
            max_duration: Maximum duration in hours
            meeting_friendly_only: Only include meeting-friendly activities
            best_for: Must be suitable for at least one of these categories

        Returns:
            Filtered activities
        """
        filtered = activities

        if tags:
            filtered = [
                a for a in filtered if any(tag in a.tags for tag in tags)
            ]

        if max_cost:
            cost_order = ["free", "budget", "moderate", "expensive", "luxury"]
            max_index = cost_order.index(max_cost.value)
            filtered = [
                a
                for a in filtered
                if cost_order.index(a.cost_level.value) <= max_index
            ]

        if min_duration is not None:
            filtered = [a for a in filtered if a.duration_hours >= min_duration]

        if max_duration is not None:
            filtered = [a for a in filtered if a.duration_hours <= max_duration]

        if meeting_friendly_only:
            filtered = [a for a in filtered if a.meeting_friendly]

        if best_for:
            filtered = [
                a for a in filtered if any(bf in a.best_for for bf in best_for)
            ]

        return filtered

    def get_popular_activities(
        self, city: str, limit: int = 10
    ) -> list[Activity]:
        """
        Get most popular activities for a city (by rating).

        Args:
            city: City name
            limit: Maximum number to return

        Returns:
            Top-rated activities
        """
        activities = self.get_activities_for_city(city)
        sorted_activities = sorted(
            activities,
            key=lambda a: a.typical_rating or 0.0,
            reverse=True,
        )
        return sorted_activities[:limit]

    def get_available_cities(self) -> list[str]:
        """
        Get list of cities with activity data.

        Returns:
            List of city names
        """
        json_files = self.data_dir.glob("*.json")
        return [f.stem.title() for f in json_files]

    def clear_cache(self):
        """Clear cached activity data."""
        self._cache.clear()
        logger.debug("Activity cache cleared")


def get_activity_repository() -> ActivityRepository:
    """Get ActivityRepository instance for dependency injection."""
    return ActivityRepository()
