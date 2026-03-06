"""Experiment and A/B testing API endpoints — fully implemented."""

from fastapi import APIRouter, Header, HTTPException, status

from wanderwing.core.event_logger import event_logger

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/summary")
async def get_experiments_summary() -> list[dict]:
    """
    Get per-variant metrics for all experiments.

    Returns a list of VariantMetrics dicts with:
    - variant, user_count
    - completion_rate, match_clickthrough_rate
    - recommendation_satisfaction, parse_correction_rate
    - funnel (event_type -> count)
    """
    metrics = event_logger.compute_metrics()
    return [m.to_dict() for m in metrics.values()]


@router.get("/ux_flow")
async def get_ux_flow_details() -> dict:
    """
    Detailed breakdown of the UX flow experiment, including funnel per variant.
    """
    metrics = event_logger.compute_metrics()
    return {
        "experiment": "ux_flow",
        "variants": {
            variant: {
                **m.to_dict(),
                "traffic_weight": _weights().get(variant, 0.0),
            }
            for variant, m in metrics.items()
        },
    }


@router.get("/ux_flow/my-variant")
async def get_my_ux_variant(x_user_id: str = Header(default="anonymous")) -> dict:
    """
    Return the variant deterministically assigned to the requesting user.

    Pass the user's session UUID in the `X-User-Id` header.
    """
    variant = event_logger.assign_variant(x_user_id)
    return {"user_id": x_user_id, "variant": variant, "experiment": "ux_flow"}


@router.post("/ux_flow/events")
async def log_ux_flow_event(
    payload: dict,
    x_user_id: str = Header(default="anonymous"),
) -> dict:
    """
    Log a single experiment event via HTTP (alternative to direct DB writes).

    Body: {"event_type": str, "metadata": dict}
    """
    event_type = payload.get("event_type")
    metadata = payload.get("metadata", {})
    if not event_type:
        raise HTTPException(status_code=400, detail="event_type is required")
    variant = event_logger.assign_variant(x_user_id)
    event_logger.log(x_user_id, variant, event_type, metadata)
    return {"ok": True, "variant": variant, "event_type": event_type}


@router.post("/events")
async def log_event(payload: dict) -> dict:
    """
    Log an event with explicit user_id.

    Body: {"user_id": str, "event_type": str, "metadata": dict}
    """
    user_id = payload.get("user_id", "anonymous")
    event_type = payload.get("event_type")
    metadata = payload.get("metadata", {})
    if not event_type:
        raise HTTPException(status_code=400, detail="event_type is required")
    variant = event_logger.assign_variant(user_id)
    event_logger.log(user_id, variant, event_type, metadata)
    return {"ok": True, "user_id": user_id, "variant": variant, "event_type": event_type}


@router.get("/active/my-assignments")
async def get_my_active_experiments(x_user_id: str = Header(default="anonymous")) -> dict:
    """
    List all active experiments and the requesting user's variant assignment.
    """
    from wanderwing.core.experiment_registry import EXPERIMENT_REGISTRY

    assignments = {}
    for exp_name, exp_config in EXPERIMENT_REGISTRY.items():
        assignments[exp_name] = {
            "variant": event_logger.assign_variant(x_user_id),
            "weights": exp_config.variants,
        }
    return {"user_id": x_user_id, "experiments": assignments}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _weights() -> dict[str, float]:
    from wanderwing.core.experiment_registry import UX_FLOW_EXPERIMENT
    return UX_FLOW_EXPERIMENT.variants
