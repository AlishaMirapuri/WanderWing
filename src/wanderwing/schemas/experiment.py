"""Experiment and A/B testing schemas."""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    """Experiment lifecycle status."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class VariantType(str, Enum):
    """Type of experiment variant."""

    CONTROL = "control"
    TREATMENT = "treatment"
    MULTI_VARIANT = "multi_variant"


class ConversionType(str, Enum):
    """Types of conversion events."""

    TRIP_CREATED = "trip_created"
    INTENT_PARSED = "intent_parsed"
    MATCH_VIEWED = "match_viewed"
    MATCH_INTERESTED = "match_interested"
    CONNECTION_REQUESTED = "connection_requested"
    CONNECTION_ACCEPTED = "connection_accepted"
    RECOMMENDATION_ACCEPTED = "recommendation_accepted"
    FEEDBACK_SUBMITTED = "feedback_submitted"


class ExperimentAssignment(BaseModel):
    """
    Assignment of a user to an experiment variant.

    This tracks which variant each user sees for A/B testing.
    """

    id: int | None = None
    experiment_name: Annotated[str, Field(min_length=3, max_length=100)]
    variant_name: Annotated[str, Field(min_length=1, max_length=50)]
    user_id: int | None = None
    session_id: Annotated[str | None, Field(max_length=100)] = None

    # Conversion tracking
    converted: bool = False
    conversion_type: ConversionType | None = None
    conversion_value: float | None = None
    converted_at: datetime | None = None

    # Metadata
    assignment_method: Annotated[str, Field(max_length=50)] = "random"
    metadata: dict[str, Any] = {}

    # Timing
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    exposure_count: int = 0
    last_exposed_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5001,
                "experiment_name": "itinerary_extraction_prompt_v2",
                "variant_name": "treatment",
                "user_id": 123,
                "session_id": "sess_abc123",
                "converted": True,
                "conversion_type": "intent_parsed",
                "conversion_value": 1.0,
                "converted_at": "2024-03-15T10:35:22Z",
                "assignment_method": "deterministic_hash",
                "metadata": {"prompt_version": "v2", "model": "gpt-4-turbo"},
                "assigned_at": "2024-03-15T10:30:00Z",
                "exposure_count": 1,
            }
        }
    }


class ExperimentVariant(BaseModel):
    """Definition of an experiment variant."""

    name: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(max_length=500)]
    allocation_percentage: Annotated[float, Field(ge=0.0, le=100.0)]
    config: dict[str, Any] = {}
    is_control: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "control",
                "description": "Original prompt with basic structure",
                "allocation_percentage": 50.0,
                "config": {"prompt_template": "extraction_v1.txt"},
                "is_control": True,
            }
        }
    }


class ExperimentDefinition(BaseModel):
    """Complete experiment definition."""

    name: Annotated[str, Field(min_length=3, max_length=100)]
    description: Annotated[str, Field(min_length=10, max_length=1000)]
    status: ExperimentStatus
    variants: Annotated[list[ExperimentVariant], Field(min_length=2, max_length=10)]
    primary_metric: Annotated[str, Field(max_length=100)]
    secondary_metrics: Annotated[list[str], Field(max_length=10)] = []

    # Targeting
    target_percentage: Annotated[float, Field(ge=0.0, le=100.0)] = 100.0
    inclusion_criteria: dict[str, Any] = {}
    exclusion_criteria: dict[str, Any] = {}

    # Timing
    start_date: datetime
    end_date: datetime | None = None
    created_by: Annotated[str, Field(max_length=100)]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "itinerary_extraction_prompt_v2",
                "description": "Test new prompt template with improved structure and few-shot examples for better itinerary extraction accuracy",
                "status": "active",
                "variants": [
                    {
                        "name": "control",
                        "description": "Original v1 prompt",
                        "allocation_percentage": 50.0,
                        "is_control": True,
                    },
                    {
                        "name": "treatment",
                        "description": "New v2 prompt with examples",
                        "allocation_percentage": 50.0,
                        "is_control": False,
                    },
                ],
                "primary_metric": "intent_parsing_success_rate",
                "secondary_metrics": ["confidence_score", "processing_time", "user_satisfaction"],
                "target_percentage": 100.0,
                "start_date": "2024-03-01T00:00:00Z",
                "end_date": "2024-04-01T00:00:00Z",
                "created_by": "product_team",
            }
        }
    }


class ExperimentMetrics(BaseModel):
    """Aggregated metrics for an experiment variant."""

    variant_name: str
    total_assignments: int
    total_conversions: int
    conversion_rate: Annotated[float, Field(ge=0.0, le=1.0)]
    avg_conversion_value: float | None = None
    confidence_interval_95: tuple[float, float] | None = None
    statistical_significance: bool | None = None
    p_value: float | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "variant_name": "treatment",
                "total_assignments": 1250,
                "total_conversions": 1087,
                "conversion_rate": 0.8696,
                "avg_conversion_value": 1.0,
                "confidence_interval_95": (0.851, 0.888),
                "statistical_significance": True,
                "p_value": 0.003,
            }
        }
    }


class ExperimentSummary(BaseModel):
    """Summary of experiment results."""

    experiment_name: str
    status: ExperimentStatus
    variants: list[ExperimentMetrics]
    winning_variant: str | None = None
    improvement_over_control: float | None = None
    started_at: datetime
    last_updated: datetime
    total_participants: int
    days_running: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "experiment_name": "itinerary_extraction_prompt_v2",
                "status": "active",
                "variants": [
                    {
                        "variant_name": "control",
                        "total_assignments": 1200,
                        "total_conversions": 960,
                        "conversion_rate": 0.80,
                    },
                    {
                        "variant_name": "treatment",
                        "total_assignments": 1250,
                        "total_conversions": 1087,
                        "conversion_rate": 0.87,
                    },
                ],
                "winning_variant": "treatment",
                "improvement_over_control": 0.0875,
                "started_at": "2024-03-01T00:00:00Z",
                "last_updated": "2024-03-15T12:00:00Z",
                "total_participants": 2450,
                "days_running": 14,
            }
        }
    }
