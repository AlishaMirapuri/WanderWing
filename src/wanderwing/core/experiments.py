"""A/B testing and experimentation framework."""

import hashlib
import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from wanderwing.db import models
from wanderwing.utils.config import get_settings
from wanderwing.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ExperimentConfig:
    """Experiment configuration."""

    def __init__(self, name: str, variants: dict[str, float]) -> None:
        """
        Initialize experiment.

        Args:
            name: Experiment name
            variants: Dict of variant_name -> weight (weights should sum to 1.0)
        """
        self.name = name
        self.variants = variants

        # Validate weights
        total_weight = sum(variants.values())
        if not (0.99 <= total_weight <= 1.01):
            logger.warning(f"Experiment {name} weights sum to {total_weight}, not 1.0")


class ExperimentTracker:
    """Track and manage A/B experiments."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.experiments = self._load_experiments()

    def _load_experiments(self) -> dict[str, ExperimentConfig]:
        """Load experiment configurations."""
        # For MVP, hardcode experiments
        # In production, load from config file or database
        return {
            "itinerary_extraction_prompt": ExperimentConfig(
                name="itinerary_extraction_prompt",
                variants={"v1": 0.5, "v2": 0.5},
            ),
            "matching_algorithm": ExperimentConfig(
                name="matching_algorithm",
                variants={"hybrid": 0.7, "llm_only": 0.3},
            ),
        }

    def get_variant(self, experiment_name: str, user_id: int) -> str:
        """
        Get experiment variant for a user (deterministic based on user_id).

        Args:
            experiment_name: Name of the experiment
            user_id: User ID

        Returns:
            Variant name
        """
        if experiment_name not in self.experiments:
            logger.warning(f"Unknown experiment: {experiment_name}")
            return "control"

        experiment = self.experiments[experiment_name]

        # Deterministic assignment based on user_id
        hash_input = f"{experiment_name}:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        assignment_value = (hash_value % 100) / 100.0

        # Select variant based on cumulative weights
        cumulative = 0.0
        for variant, weight in experiment.variants.items():
            cumulative += weight
            if assignment_value <= cumulative:
                return variant

        # Fallback to first variant
        return list(experiment.variants.keys())[0]

    def track_assignment(
        self,
        experiment_name: str,
        variant: str,
        user_id: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track experiment assignment."""
        experiment_record = models.Experiment(
            name=experiment_name,
            variant=variant,
            user_id=user_id,
            metadata=metadata or {},
        )
        self.db.add(experiment_record)
        self.db.commit()

    def track_conversion(
        self,
        experiment_name: str,
        user_id: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Mark experiment as converted for user."""
        # Find most recent experiment record
        result = (
            self.db.query(models.Experiment)
            .filter(
                models.Experiment.name == experiment_name,
                models.Experiment.user_id == user_id,
            )
            .order_by(models.Experiment.created_at.desc())
            .first()
        )

        if result:
            result.converted = True
            if metadata:
                result.metadata.update(metadata)
            self.db.commit()


def get_experiment_variant(
    db: Session,
    experiment_name: str,
    user_id: int,
) -> str:
    """
    Get variant for user in experiment.

    Args:
        db: Database session
        experiment_name: Experiment name
        user_id: User ID

    Returns:
        Variant name
    """
    if not settings.enable_experiments:
        return "control"

    tracker = ExperimentTracker(db)
    variant = tracker.get_variant(experiment_name, user_id)

    # Track assignment
    tracker.track_assignment(experiment_name, variant, user_id)

    return variant
