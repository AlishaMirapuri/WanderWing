"""
Unit tests for the WanderWing experimentation framework.

Tests:
- Deterministic variant assignment
- Variant distribution across 100 IDs within ±10% of target weights
- Event logging writes to DB (in-memory SQLite)
- Metrics computation correctness
- Edge cases: zero division, empty DB, parse_correction_rate
"""

import uuid
from collections import Counter

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from wanderwing.core.event_logger import EventLogger, VariantMetrics, _events_table, _metadata
from wanderwing.core.experiment_registry import UX_FLOW_EXPERIMENT


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def in_memory_logger():
    """
    Return an EventLogger backed by a fresh in-memory SQLite database.

    Monkeypatches EventLogger to use an isolated engine so tests don't
    touch the real wanderwing.db file.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    _metadata.create_all(engine, checkfirst=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    logger = EventLogger()
    # Override the module-level session factory and engine via the instance
    import wanderwing.core.event_logger as el_module
    original_engine = el_module._engine
    original_session = el_module._SessionLocal
    el_module._engine = engine
    el_module._SessionLocal = SessionLocal

    yield logger

    # Restore
    el_module._engine = original_engine
    el_module._SessionLocal = original_session
    engine.dispose()


# ── Variant assignment tests ───────────────────────────────────────────────────


class TestVariantAssignment:
    def test_same_user_always_gets_same_variant(self, in_memory_logger):
        """Variant assignment must be deterministic."""
        user_id = "user-stable-123"
        v1 = in_memory_logger.assign_variant(user_id)
        v2 = in_memory_logger.assign_variant(user_id)
        v3 = in_memory_logger.assign_variant(user_id)
        assert v1 == v2 == v3

    def test_variant_is_valid(self, in_memory_logger):
        """Assigned variant must be one of the registered variants."""
        valid_variants = set(UX_FLOW_EXPERIMENT.variants.keys())
        for _ in range(50):
            uid = str(uuid.uuid4())
            assert in_memory_logger.assign_variant(uid) in valid_variants

    def test_distribution_within_tolerance(self, in_memory_logger):
        """
        Over 100 unique user IDs, each variant should be within ±10 percentage
        points of its target weight.
        """
        n = 100
        counts = Counter(
            in_memory_logger.assign_variant(f"user-dist-{i:04d}") for i in range(n)
        )
        for variant, target_weight in UX_FLOW_EXPERIMENT.variants.items():
            actual_pct = counts[variant] / n
            assert abs(actual_pct - target_weight) <= 0.10, (
                f"{variant}: got {actual_pct:.0%}, expected {target_weight:.0%} ±10%"
            )

    def test_different_users_can_get_different_variants(self, in_memory_logger):
        """At least 2 distinct variants should appear across 20 different users."""
        variants_seen = {in_memory_logger.assign_variant(f"u{i}") for i in range(20)}
        assert len(variants_seen) >= 2


# ── Event logging tests ───────────────────────────────────────────────────────


class TestEventLogging:
    def test_log_writes_to_db(self, in_memory_logger):
        """log() should write a row to the DB."""
        in_memory_logger.log("user-1", "variant_a", "profile_completed", {"name": "Alice"})
        events = in_memory_logger.get_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "profile_completed"
        assert events[0]["user_id"] == "user-1"

    def test_log_multiple_events(self, in_memory_logger):
        """Multiple log() calls should produce multiple rows."""
        for et in ["profile_completed", "parse_accepted", "match_clicked"]:
            in_memory_logger.log("user-multi", "variant_b", et, {})
        events = in_memory_logger.get_events(variant="variant_b")
        assert len(events) == 3

    def test_get_events_filtered_by_variant(self, in_memory_logger):
        """get_events(variant=) should return only that variant's events."""
        in_memory_logger.log("u1", "variant_a", "profile_completed", {})
        in_memory_logger.log("u2", "variant_b", "profile_completed", {})
        in_memory_logger.log("u3", "variant_c", "profile_completed", {})

        va_events = in_memory_logger.get_events(variant="variant_a")
        assert len(va_events) == 1
        assert all(e["variant"] == "variant_a" for e in va_events)

    def test_get_events_filtered_by_event_type(self, in_memory_logger):
        """get_events(event_type=) should return only that event type."""
        in_memory_logger.log("u1", "variant_a", "profile_completed", {})
        in_memory_logger.log("u1", "variant_a", "parse_accepted", {})
        in_memory_logger.log("u1", "variant_a", "feedback_submitted", {})

        feedback_events = in_memory_logger.get_events(event_type="feedback_submitted")
        assert len(feedback_events) == 1
        assert feedback_events[0]["event_type"] == "feedback_submitted"

    def test_metadata_is_stored_and_retrieved(self, in_memory_logger):
        """metadata dict should survive the round-trip to DB."""
        meta = {"rating": 5, "accepted": True, "match_id": "m42"}
        in_memory_logger.log("u-meta", "variant_a", "feedback_submitted", meta)
        events = in_memory_logger.get_events(event_type="feedback_submitted")
        assert events[0]["metadata_"]["rating"] == 5
        assert events[0]["metadata_"]["match_id"] == "m42"


# ── Metrics computation tests ─────────────────────────────────────────────────


class TestMetricsComputation:
    def _seed_variant(self, logger, variant, events_per_user):
        """Helper: log events for multiple users in a variant."""
        for user_id, event_types in events_per_user.items():
            for et in event_types:
                meta = {"rating": 1} if et == "recommendation_liked" else {}
                logger.log(user_id, variant, et, meta)

    def test_completion_rate(self, in_memory_logger):
        """completion_rate = users with feedback_submitted / users with profile_completed."""
        # 4 users complete profile, 2 submit feedback
        self._seed_variant(
            in_memory_logger,
            "variant_a",
            {
                "u1": ["profile_completed", "parse_accepted", "feedback_submitted"],
                "u2": ["profile_completed", "parse_accepted", "feedback_submitted"],
                "u3": ["profile_completed", "parse_accepted"],
                "u4": ["profile_completed"],
            },
        )
        metrics = in_memory_logger.compute_metrics()
        assert metrics["variant_a"].user_count == 4
        assert metrics["variant_a"].completion_rate == pytest.approx(0.5, abs=0.01)

    def test_match_clickthrough_rate(self, in_memory_logger):
        """match_clickthrough_rate = users with match_clicked / users with parse_accepted."""
        self._seed_variant(
            in_memory_logger,
            "variant_b",
            {
                "ub1": ["parse_accepted", "match_clicked"],
                "ub2": ["parse_accepted", "match_clicked"],
                "ub3": ["parse_accepted"],
                "ub4": ["parse_accepted"],
            },
        )
        metrics = in_memory_logger.compute_metrics()
        assert metrics["variant_b"].match_clickthrough_rate == pytest.approx(0.5, abs=0.01)

    def test_recommendation_satisfaction(self, in_memory_logger):
        """recommendation_satisfaction = mean(rating) from recommendation_liked events."""
        # Log 3 liked events, all with rating=1
        for i in range(3):
            in_memory_logger.log(
                f"uc{i}", "variant_c", "recommendation_liked", {"rating": 1}
            )
        metrics = in_memory_logger.compute_metrics()
        assert metrics["variant_c"].recommendation_satisfaction == pytest.approx(1.0, abs=0.01)

    def test_parse_correction_rate(self, in_memory_logger):
        """parse_correction_rate = parse_edited users / (parse_accepted + parse_edited users)."""
        # 3 users accepted, 1 user edited (and accepted), so denom = 3+1 = 4, rate = 1/4 = 0.25
        self._seed_variant(
            in_memory_logger,
            "variant_a",
            {
                "ua1": ["parse_accepted"],
                "ua2": ["parse_accepted"],
                "ua3": ["parse_accepted"],
                "ua4": ["parse_edited", "parse_accepted"],
            },
        )
        metrics = in_memory_logger.compute_metrics()
        # parse_edited users = 1, parse_accepted users = 4 (including ua4), denom = 4+1 = 5
        # correction_rate = 1/5 = 0.20
        assert metrics["variant_a"].parse_correction_rate == pytest.approx(0.20, abs=0.01)

    def test_parse_correction_rate_zero_division(self, in_memory_logger):
        """parse_correction_rate should be 0.0 when no parse events exist."""
        # Log only profile_completed for variant_c — no parse events
        in_memory_logger.log("u-alone", "variant_c", "profile_completed", {})
        metrics = in_memory_logger.compute_metrics()
        assert metrics["variant_c"].parse_correction_rate == 0.0

    def test_empty_variant_returns_zeros(self, in_memory_logger):
        """A variant with no events should have all-zero metrics."""
        # Only seed variant_a, leave variant_b and variant_c empty
        in_memory_logger.log("u1", "variant_a", "profile_completed", {})
        metrics = in_memory_logger.compute_metrics()

        for variant in ["variant_b", "variant_c"]:
            m = metrics[variant]
            assert m.user_count == 0
            assert m.completion_rate == 0.0
            assert m.match_clickthrough_rate == 0.0
            assert m.recommendation_satisfaction == 0.0
            assert m.parse_correction_rate == 0.0

    def test_funnel_counts_are_raw_event_counts(self, in_memory_logger):
        """funnel dict should count total event rows, not unique users."""
        # User logs 3 recommendation_liked events
        for _ in range(3):
            in_memory_logger.log("u-funnel", "variant_a", "recommendation_liked", {"rating": 1})
        metrics = in_memory_logger.compute_metrics()
        assert metrics["variant_a"].funnel.get("recommendation_liked", 0) == 3

    def test_metrics_returns_all_three_variants(self, in_memory_logger):
        """compute_metrics() must always return all 3 variants."""
        metrics = in_memory_logger.compute_metrics()
        assert set(metrics.keys()) == {"variant_a", "variant_b", "variant_c"}

    def test_to_dict_serializable(self, in_memory_logger):
        """VariantMetrics.to_dict() should return a plain dict."""
        metrics = in_memory_logger.compute_metrics()
        for m in metrics.values():
            d = m.to_dict()
            assert isinstance(d, dict)
            assert "completion_rate" in d
            assert "funnel" in d
            assert isinstance(d["funnel"], dict)


# ── Experiment registry tests ──────────────────────────────────────────────────


class TestExperimentRegistry:
    def test_weights_sum_to_one(self):
        """Traffic weights must sum to exactly 1.0."""
        total = sum(UX_FLOW_EXPERIMENT.variants.values())
        assert abs(total - 1.0) < 0.001

    def test_three_variants_defined(self):
        assert len(UX_FLOW_EXPERIMENT.variants) == 3
        assert "variant_a" in UX_FLOW_EXPERIMENT.variants
        assert "variant_b" in UX_FLOW_EXPERIMENT.variants
        assert "variant_c" in UX_FLOW_EXPERIMENT.variants
