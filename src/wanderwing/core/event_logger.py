"""
Event logger for the WanderWing experimentation framework.

Self-contained module importable from both the Streamlit frontend and FastAPI.
Creates its own SQLAlchemy engine from settings so it does NOT trigger the
db/__init__.py import chain (which requires the optional email-validator package).

Usage:
    from wanderwing.core.event_logger import event_logger

    variant = event_logger.assign_variant("user-uuid")
    event_logger.log("user-uuid", variant, "profile_completed", {"name": "Alice"})
    metrics = event_logger.compute_metrics()
"""

import hashlib
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import sessionmaker

from wanderwing.core.experiment_registry import UX_FLOW_EXPERIMENT
from wanderwing.utils.config import get_settings

# ── Engine (standalone — does not import wanderwing.db to avoid schema chain) ─

_settings = get_settings()
_engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False} if _settings.is_sqlite else {},
)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# ── Table definition ──────────────────────────────────────────────────────────
# Mirrors the ExperimentEvent ORM model in wanderwing.db.models without
# importing it (which would pull in the email-validator dependency chain).

_metadata = MetaData()

_events_table = Table(
    "experiment_events",
    _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String(255), nullable=False, index=True),
    Column("variant", String(20), nullable=False, index=True),
    Column("event_type", String(50), nullable=False, index=True),
    Column("metadata_", JSON, nullable=False, default={}),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)

# Create the table if it doesn't yet exist (idempotent)
_metadata.create_all(_engine, checkfirst=True)

# ── Constants ─────────────────────────────────────────────────────────────────

VALID_EVENT_TYPES = {
    "profile_completed",
    "parse_accepted",
    "parse_edited",
    "match_clicked",
    "recommendation_liked",
    "feedback_submitted",
}

# ── Types ─────────────────────────────────────────────────────────────────────


@dataclass
class VariantMetrics:
    """Aggregated metrics for one experiment variant."""

    variant: str
    user_count: int
    completion_rate: float              # feedback_submitted users / profile_completed users
    match_clickthrough_rate: float      # match_clicked users / parse_accepted users
    recommendation_satisfaction: float  # mean rating from recommendation_liked events
    parse_correction_rate: float        # parse_edited users / (parse_accepted + parse_edited users)
    funnel: dict[str, int] = field(default_factory=dict)  # event_type -> raw count

    def to_dict(self) -> dict:
        return {
            "variant": self.variant,
            "user_count": self.user_count,
            "completion_rate": self.completion_rate,
            "match_clickthrough_rate": self.match_clickthrough_rate,
            "recommendation_satisfaction": self.recommendation_satisfaction,
            "parse_correction_rate": self.parse_correction_rate,
            "funnel": self.funnel,
        }


# ── EventLogger ───────────────────────────────────────────────────────────────


class EventLogger:
    """
    Reads and writes experiment events to the experiment_events table.

    Thread-safe: each public method opens and closes its own session.
    """

    # ── Variant assignment ────────────────────────────────────────────────────

    def assign_variant(self, user_id: str) -> str:
        """
        Deterministically assign a UX variant via MD5 bucket hashing.

        The same user_id always maps to the same variant for the lifetime of the
        experiment weight configuration. No DB write is performed.

        Args:
            user_id: Any string identifier (UUID, session token, synthetic ID)

        Returns:
            Variant name — one of "variant_a", "variant_b", "variant_c"
        """
        hash_input = f"{UX_FLOW_EXPERIMENT.name}:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        bucket = (hash_value % 100) / 100.0

        cumulative = 0.0
        for variant, weight in UX_FLOW_EXPERIMENT.variants.items():
            cumulative += weight
            if bucket < cumulative:
                return variant

        # Fallback — should never be reached if weights sum to 1.0
        return list(UX_FLOW_EXPERIMENT.variants.keys())[0]

    # ── Write ─────────────────────────────────────────────────────────────────

    def log(
        self,
        user_id: str,
        variant: str,
        event_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Write one experiment event row to the database.

        Args:
            user_id: String user identifier
            variant: Variant name (e.g., "variant_a")
            event_type: One of VALID_EVENT_TYPES
            metadata: Optional JSON-serialisable context dict
        """
        db = _SessionLocal()
        try:
            db.execute(
                _events_table.insert().values(
                    user_id=user_id,
                    variant=variant,
                    event_type=event_type,
                    metadata_=metadata or {},
                )
            )
            db.commit()
        finally:
            db.close()

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_events(
        self,
        variant: str | None = None,
        event_type: str | None = None,
    ) -> list[dict]:
        """
        Retrieve events, optionally filtered by variant and/or event_type.

        Returns:
            List of dicts: id, user_id, variant, event_type, metadata_, created_at
        """
        db = _SessionLocal()
        try:
            stmt = select(_events_table)
            if variant is not None:
                stmt = stmt.where(_events_table.c.variant == variant)
            if event_type is not None:
                stmt = stmt.where(_events_table.c.event_type == event_type)
            stmt = stmt.order_by(_events_table.c.created_at)
            rows = db.execute(stmt).mappings().all()
            return [
                {
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "variant": r["variant"],
                    "event_type": r["event_type"],
                    "metadata_": r["metadata_"],
                    "created_at": str(r["created_at"]) if r["created_at"] else None,
                }
                for r in rows
            ]
        finally:
            db.close()

    # ── Metrics ───────────────────────────────────────────────────────────────

    def compute_metrics(self) -> dict[str, VariantMetrics]:
        """
        Compute all 4 key metrics per variant from the event store.

        Definitions
        -----------
        completion_rate        : users with feedback_submitted / users with profile_completed
        match_clickthrough_rate: users with match_clicked / users with parse_accepted
        recommendation_satisfaction: mean(rating) from recommendation_liked events
        parse_correction_rate  : users with parse_edited / (parse_accepted + parse_edited users)

        Returns
        -------
        Dict mapping variant name -> VariantMetrics
        """
        db = _SessionLocal()
        try:
            results: dict[str, VariantMetrics] = {}

            for variant in UX_FLOW_EXPERIMENT.variants:
                stmt = select(_events_table).where(_events_table.c.variant == variant)
                rows = db.execute(stmt).mappings().all()

                if not rows:
                    results[variant] = VariantMetrics(
                        variant=variant,
                        user_count=0,
                        completion_rate=0.0,
                        match_clickthrough_rate=0.0,
                        recommendation_satisfaction=0.0,
                        parse_correction_rate=0.0,
                        funnel={},
                    )
                    continue

                # Build per-user event sets for unique-user metrics
                per_user_events: dict[str, set[str]] = {}
                funnel_counts: dict[str, int] = {et: 0 for et in VALID_EVENT_TYPES}
                rec_ratings: list[float] = []
                all_users: set[str] = set()

                for row in rows:
                    uid = row["user_id"]
                    et = row["event_type"]
                    all_users.add(uid)
                    if et in VALID_EVENT_TYPES:
                        per_user_events.setdefault(uid, set()).add(et)
                        funnel_counts[et] += 1
                    if et == "recommendation_liked":
                        rating = (row["metadata_"] or {}).get("rating", 1)
                        rec_ratings.append(float(rating))

                def _users_with(event: str) -> int:
                    return sum(1 for evts in per_user_events.values() if event in evts)

                n_profile = _users_with("profile_completed")
                n_feedback = _users_with("feedback_submitted")
                n_parse_accepted = _users_with("parse_accepted")
                n_match_clicked = _users_with("match_clicked")
                n_parse_edited = _users_with("parse_edited")

                completion_rate = n_feedback / n_profile if n_profile > 0 else 0.0

                match_ctr = (
                    n_match_clicked / n_parse_accepted if n_parse_accepted > 0 else 0.0
                )

                rec_satisfaction = (
                    sum(rec_ratings) / len(rec_ratings) if rec_ratings else 0.0
                )

                correction_denom = n_parse_accepted + n_parse_edited
                parse_correction_rate = (
                    n_parse_edited / correction_denom if correction_denom > 0 else 0.0
                )

                results[variant] = VariantMetrics(
                    variant=variant,
                    user_count=len(all_users),
                    completion_rate=round(completion_rate, 4),
                    match_clickthrough_rate=round(match_ctr, 4),
                    recommendation_satisfaction=round(rec_satisfaction, 4),
                    parse_correction_rate=round(parse_correction_rate, 4),
                    funnel=funnel_counts,
                )

            return results
        finally:
            db.close()


# Module-level singleton — import this everywhere
event_logger = EventLogger()
