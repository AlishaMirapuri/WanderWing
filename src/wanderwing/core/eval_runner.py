"""
Behavioral Eval Framework for WanderWing prompts.

Runs structured test cases against a parser function (mock or real LLM) and
persists reports to SQLite for regression detection across runs.

Standalone module — creates its own SQLAlchemy engine.

Usage:
    from wanderwing.core.eval_runner import EvalRunner
    from wanderwing.frontend.utils.mock_data import generate_parsed_intent

    runner = EvalRunner()
    report = runner.run("intent_extraction", generate_parsed_intent)
    previous = runner.load_previous_report("intent_extraction")
    runner.store_report(report)
    alerts = runner.detect_regressions(report, previous)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Literal, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import sessionmaker

from wanderwing.utils.config import get_settings

# ── Engine ────────────────────────────────────────────────────────────────────

_settings = get_settings()
_engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False} if _settings.is_sqlite else {},
)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# ── Tables ────────────────────────────────────────────────────────────────────

_metadata = MetaData()

_reports_table = Table(
    "eval_reports",
    _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("prompt_name", String(255), nullable=False, index=True),
    Column("prompt_hash", String(64), nullable=False),
    Column("total", Integer, nullable=False),
    Column("passed", Integer, nullable=False),
    Column("overall_score", Float, nullable=False),
    Column("results_json", Text, nullable=False),
    Column("run_at", DateTime, nullable=False),
)

_metadata.create_all(_engine, checkfirst=True)

# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class AssertionResult:
    name: str
    passed: bool
    score: float  # 0.0 or 1.0
    reason: str


@dataclass
class EvalResult:
    test_case_id: str
    test_case_name: str
    prompt_hash: str
    score: float           # mean of assertion scores
    passed: bool           # score >= pass_threshold
    assertion_results: list[AssertionResult] = field(default_factory=list)


@dataclass
class EvalReport:
    prompt_name: str
    prompt_hash: str
    total: int
    passed: int
    overall_score: float   # mean of per-test-case scores
    results: list[EvalResult] = field(default_factory=list)
    run_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RegressionAlert:
    test_case_id: str
    test_case_name: str
    previous_score: float
    current_score: float
    delta: float           # current - previous (negative = regression)
    severity: Literal["critical", "warning"]


# ── Test cases ────────────────────────────────────────────────────────────────
# Designed to work with generate_parsed_intent() mock AND real LLM.
# Each test case is a dict with: id, name, input, assertions
# Each assertion is a callable (result_dict) -> AssertionResult


def _assert(name: str, condition: bool, reason_pass: str, reason_fail: str) -> AssertionResult:
    return AssertionResult(
        name=name,
        passed=condition,
        score=1.0 if condition else 0.0,
        reason=reason_pass if condition else reason_fail,
    )


def _destination_contains(result: dict, keyword: str) -> bool:
    dest = (result.get("primary_destination") or "").lower()
    return keyword.lower() in dest


def _has_activity(result: dict, activity: str) -> bool:
    activities = [a.upper() for a in (result.get("activities") or [])]
    return activity.upper() in activities


def _has_any_activity(result: dict, *activities: str) -> bool:
    result_activities = [a.upper() for a in (result.get("activities") or [])]
    return any(a.upper() in result_activities for a in activities)


TEST_CASES: list[dict[str, Any]] = [
    {
        "id": "TC01",
        "name": "Tokyo hiking food relaxed",
        "input": "Tokyo 10 days hiking food relaxed",
        "assertions": [
            lambda r: _assert(
                "destination_tokyo",
                _destination_contains(r, "Tokyo"),
                "primary_destination contains 'Tokyo'",
                f"Expected destination Tokyo, got: {r.get('primary_destination')}",
            ),
            lambda r: _assert(
                "activity_hiking",
                _has_activity(r, "HIKING"),
                "HIKING found in activities",
                f"HIKING not in activities: {r.get('activities')}",
            ),
            lambda r: _assert(
                "pace_relaxed",
                (r.get("pace_preference") or "").upper() == "RELAXED",
                "pace_preference is RELAXED",
                f"Expected RELAXED pace, got: {r.get('pace_preference')}",
            ),
        ],
    },
    {
        "id": "TC02",
        "name": "Paris museums weekend",
        "input": "Paris museums weekend",
        "assertions": [
            lambda r: _assert(
                "destination_paris",
                _destination_contains(r, "Paris"),
                "primary_destination contains 'Paris'",
                f"Expected destination Paris, got: {r.get('primary_destination')}",
            ),
            lambda r: _assert(
                "activity_museums",
                _has_activity(r, "MUSEUMS"),
                "MUSEUMS found in activities",
                f"MUSEUMS not in activities: {r.get('activities')}",
            ),
        ],
    },
    {
        "id": "TC03",
        "name": "Barcelona beach food budget",
        "input": "Barcelona beach food budget cheap",
        "assertions": [
            lambda r: _assert(
                "destination_barcelona",
                _destination_contains(r, "Barcelona"),
                "primary_destination contains 'Barcelona'",
                f"Expected destination Barcelona, got: {r.get('primary_destination')}",
            ),
            lambda r: _assert(
                "activity_food_tours",
                _has_activity(r, "FOOD_TOURS"),
                "FOOD_TOURS found in activities",
                f"FOOD_TOURS not in activities: {r.get('activities')}",
            ),
            lambda r: _assert(
                "budget_tier",
                (r.get("budget_tier") or "").upper() == "BUDGET",
                "budget_tier is BUDGET",
                f"Expected BUDGET, got: {r.get('budget_tier')}",
            ),
        ],
    },
    {
        "id": "TC04",
        "name": "London nightlife fast culture",
        "input": "London nightlife fast-paced culture",
        "assertions": [
            lambda r: _assert(
                "destination_london",
                _destination_contains(r, "London"),
                "primary_destination contains 'London'",
                f"Expected destination London, got: {r.get('primary_destination')}",
            ),
            lambda r: _assert(
                "activity_nightlife",
                _has_activity(r, "NIGHTLIFE"),
                "NIGHTLIFE found in activities",
                f"NIGHTLIFE not in activities: {r.get('activities')}",
            ),
            lambda r: _assert(
                "pace_fast",
                (r.get("pace_preference") or "").upper() == "FAST",
                "pace_preference is FAST",
                f"Expected FAST pace, got: {r.get('pace_preference')}",
            ),
        ],
    },
    {
        "id": "TC05",
        "name": "New York shopping adventure",
        "input": "New York City shopping adventure",
        "assertions": [
            lambda r: _assert(
                "destination_new_york",
                _destination_contains(r, "New York"),
                "primary_destination contains 'New York'",
                f"Expected destination New York, got: {r.get('primary_destination')}",
            ),
            lambda r: _assert(
                "activity_shopping_or_adventure",
                _has_any_activity(r, "SHOPPING", "ADVENTURE_SPORTS"),
                "SHOPPING or ADVENTURE_SPORTS in activities",
                f"Neither SHOPPING nor ADVENTURE_SPORTS in activities: {r.get('activities')}",
            ),
        ],
    },
    {
        "id": "TC06",
        "name": "Tokyo luxury budget tier",
        "input": "Tokyo luxury 5-star hotels",
        "assertions": [
            lambda r: _assert(
                "budget_comfortable",
                (r.get("budget_tier") or "").upper() in ("COMFORTABLE", "LUXURY"),
                "budget_tier is COMFORTABLE or LUXURY",
                f"Expected COMFORTABLE/LUXURY for luxury input, got: {r.get('budget_tier')}",
            ),
        ],
    },
    {
        "id": "TC07",
        "name": "Barcelona hiking relaxed",
        "input": "Barcelona hiking mountains relaxed",
        "assertions": [
            lambda r: _assert(
                "destination_barcelona",
                _destination_contains(r, "Barcelona"),
                "primary_destination contains 'Barcelona'",
                f"Expected destination Barcelona, got: {r.get('primary_destination')}",
            ),
            lambda r: _assert(
                "activity_hiking",
                _has_activity(r, "HIKING"),
                "HIKING found in activities",
                f"HIKING not in activities: {r.get('activities')}",
            ),
            lambda r: _assert(
                "pace_relaxed",
                (r.get("pace_preference") or "").upper() == "RELAXED",
                "pace_preference is RELAXED",
                f"Expected RELAXED pace, got: {r.get('pace_preference')}",
            ),
        ],
    },
    {
        "id": "TC08",
        "name": "Schema validity check",
        "input": "Tokyo 5 days",
        "assertions": [
            lambda r: _assert(
                "confidence_range",
                0.0 <= float(r.get("confidence_score", -1)) <= 1.0,
                "confidence_score is in [0.0, 1.0]",
                f"confidence_score out of range: {r.get('confidence_score')}",
            ),
            lambda r: _assert(
                "activities_is_list",
                isinstance(r.get("activities"), list),
                "activities is a list",
                f"activities is not a list: {type(r.get('activities'))}",
            ),
            lambda r: _assert(
                "destination_is_string",
                isinstance(r.get("primary_destination"), str)
                and len(r.get("primary_destination", "")) > 0,
                "primary_destination is a non-empty string",
                f"primary_destination invalid: {r.get('primary_destination')}",
            ),
        ],
    },
    {
        "id": "TC09",
        "name": "Paris fast-paced multi-activity",
        "input": "Paris fast-paced art culture shopping",
        "assertions": [
            lambda r: _assert(
                "pace_fast",
                (r.get("pace_preference") or "").upper() == "FAST",
                "pace_preference is FAST",
                f"Expected FAST pace, got: {r.get('pace_preference')}",
            ),
            lambda r: _assert(
                "at_least_2_activities",
                len(r.get("activities") or []) >= 2,
                f"at least 2 activities detected (got {len(r.get('activities') or [])})",
                f"Only {len(r.get('activities') or [])} activities detected: {r.get('activities')}",
            ),
        ],
    },
    {
        "id": "TC10",
        "name": "Tokyo multi-activity detection",
        "input": "Tokyo food ramen hiking adventure",
        "assertions": [
            lambda r: _assert(
                "at_least_3_unique_activities",
                len(set(r.get("activities") or [])) >= 3,
                f"at least 3 unique activities (got {len(set(r.get('activities') or []))})",
                f"Only {len(set(r.get('activities') or []))} unique activities: {r.get('activities')}",
            ),
        ],
    },
]


# ── Serialization helpers ─────────────────────────────────────────────────────


def _serialize_results(results: list[EvalResult]) -> str:
    return json.dumps(
        [
            {
                "test_case_id": r.test_case_id,
                "test_case_name": r.test_case_name,
                "prompt_hash": r.prompt_hash,
                "score": r.score,
                "passed": r.passed,
                "assertion_results": [
                    {
                        "name": a.name,
                        "passed": a.passed,
                        "score": a.score,
                        "reason": a.reason,
                    }
                    for a in r.assertion_results
                ],
            }
            for r in results
        ]
    )


def _deserialize_results(json_str: str) -> list[EvalResult]:
    data = json.loads(json_str)
    return [
        EvalResult(
            test_case_id=r["test_case_id"],
            test_case_name=r["test_case_name"],
            prompt_hash=r["prompt_hash"],
            score=r["score"],
            passed=r["passed"],
            assertion_results=[
                AssertionResult(
                    name=a["name"],
                    passed=a["passed"],
                    score=a["score"],
                    reason=a["reason"],
                )
                for a in r["assertion_results"]
            ],
        )
        for r in data
    ]


# ── EvalRunner ────────────────────────────────────────────────────────────────


class EvalRunner:
    """
    Runs behavioral test cases against a parser function and detects regressions.

    The parser_fn takes a raw text string and returns a dict with fields like
    primary_destination, activities, budget_tier, pace_preference, confidence_score.

    Compatible with both generate_parsed_intent() (mock, no API keys) and
    the real IntentParser.
    """

    def run(
        self,
        prompt_name: str,
        parser_fn: Callable[[str], dict],
        pass_threshold: float = 0.75,
        prompt_hash: str = "mock",
    ) -> EvalReport:
        """
        Run all test cases for a given prompt name.

        Args:
            prompt_name: Logical prompt identifier (e.g., "intent_extraction")
            parser_fn: Callable that parses raw text → result dict
            pass_threshold: Minimum score for a test case to be counted as passing
            prompt_hash: SHA256 hash of the prompt text (or "mock" for mock parser)

        Returns:
            EvalReport with per-test-case results and aggregate statistics
        """
        results: list[EvalResult] = []

        for tc in TEST_CASES:
            try:
                parsed = parser_fn(tc["input"])
            except Exception as e:
                # Parser error → all assertions fail
                assertion_results = [
                    AssertionResult(
                        name="parser_error",
                        passed=False,
                        score=0.0,
                        reason=f"Parser raised exception: {e}",
                    )
                ]
                results.append(
                    EvalResult(
                        test_case_id=tc["id"],
                        test_case_name=tc["name"],
                        prompt_hash=prompt_hash,
                        score=0.0,
                        passed=False,
                        assertion_results=assertion_results,
                    )
                )
                continue

            assertion_results: list[AssertionResult] = []
            for assertion_fn in tc["assertions"]:
                try:
                    ar = assertion_fn(parsed)
                except Exception as e:
                    ar = AssertionResult(
                        name="assertion_error",
                        passed=False,
                        score=0.0,
                        reason=f"Assertion raised exception: {e}",
                    )
                assertion_results.append(ar)

            score = (
                sum(a.score for a in assertion_results) / len(assertion_results)
                if assertion_results
                else 0.0
            )
            results.append(
                EvalResult(
                    test_case_id=tc["id"],
                    test_case_name=tc["name"],
                    prompt_hash=prompt_hash,
                    score=round(score, 4),
                    passed=score >= pass_threshold,
                    assertion_results=assertion_results,
                )
            )

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        overall_score = (
            round(sum(r.score for r in results) / total, 4) if total > 0 else 0.0
        )

        return EvalReport(
            prompt_name=prompt_name,
            prompt_hash=prompt_hash,
            total=total,
            passed=passed,
            overall_score=overall_score,
            results=results,
            run_at=datetime.utcnow(),
        )

    def store_report(self, report: EvalReport) -> None:
        """
        Persist an EvalReport to the eval_reports table.
        """
        db = _SessionLocal()
        try:
            db.execute(
                _reports_table.insert().values(
                    prompt_name=report.prompt_name,
                    prompt_hash=report.prompt_hash,
                    total=report.total,
                    passed=report.passed,
                    overall_score=report.overall_score,
                    results_json=_serialize_results(report.results),
                    run_at=report.run_at,
                )
            )
            db.commit()
        finally:
            db.close()

    def load_previous_report(self, prompt_name: str) -> Optional[EvalReport]:
        """
        Load the most recently stored EvalReport for a prompt name.

        Call this BEFORE store_report() in the same run to get the report
        from the previous run (not the one you are about to store).

        Returns:
            EvalReport or None if no previous report exists
        """
        db = _SessionLocal()
        try:
            row = (
                db.execute(
                    select(_reports_table)
                    .where(_reports_table.c.prompt_name == prompt_name)
                    .order_by(_reports_table.c.run_at.desc())
                    .limit(1)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return EvalReport(
                prompt_name=row["prompt_name"],
                prompt_hash=row["prompt_hash"],
                total=row["total"],
                passed=row["passed"],
                overall_score=row["overall_score"],
                results=_deserialize_results(row["results_json"]),
                run_at=row["run_at"],
            )
        finally:
            db.close()

    def load_all_reports(self, prompt_name: str) -> list[EvalReport]:
        """
        Load all stored reports for a prompt name, newest first.
        """
        db = _SessionLocal()
        try:
            rows = (
                db.execute(
                    select(_reports_table)
                    .where(_reports_table.c.prompt_name == prompt_name)
                    .order_by(_reports_table.c.run_at.desc())
                )
                .mappings()
                .all()
            )
            return [
                EvalReport(
                    prompt_name=row["prompt_name"],
                    prompt_hash=row["prompt_hash"],
                    total=row["total"],
                    passed=row["passed"],
                    overall_score=row["overall_score"],
                    results=_deserialize_results(row["results_json"]),
                    run_at=row["run_at"],
                )
                for row in rows
            ]
        finally:
            db.close()

    def detect_regressions(
        self,
        current: EvalReport,
        previous: Optional[EvalReport],
        warn_threshold: float = 0.05,
        critical_threshold: float = 0.20,
    ) -> list[RegressionAlert]:
        """
        Compare two EvalReports and return regression alerts for score drops.

        A test case is flagged when its score has decreased by more than
        warn_threshold. A drop larger than critical_threshold is "critical";
        otherwise "warning".

        Improvements (positive delta) are never flagged.

        Args:
            current: The newly computed EvalReport
            previous: The prior stored EvalReport (may be None → returns [])
            warn_threshold: Minimum score drop to generate a warning
            critical_threshold: Score drop magnitude that triggers critical severity

        Returns:
            List of RegressionAlert (empty if no regressions or no prior run)
        """
        if previous is None:
            return []

        prev_scores: dict[str, float] = {
            r.test_case_id: r.score for r in previous.results
        }

        alerts: list[RegressionAlert] = []
        for result in current.results:
            prev_score = prev_scores.get(result.test_case_id)
            if prev_score is None:
                continue  # new test case — not a regression
            delta = result.score - prev_score
            if delta >= -warn_threshold:
                continue  # no meaningful regression
            severity: Literal["critical", "warning"] = (
                "critical" if abs(delta) >= critical_threshold else "warning"
            )
            alerts.append(
                RegressionAlert(
                    test_case_id=result.test_case_id,
                    test_case_name=result.test_case_name,
                    previous_score=prev_score,
                    current_score=result.score,
                    delta=round(delta, 4),
                    severity=severity,
                )
            )

        return alerts
