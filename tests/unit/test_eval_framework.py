"""
Unit tests for the Prompt Version Registry + Eval Regression Framework.

Tests:
  - Hash consistency (same text → same hash)
  - Deduplication (re-registering same text does not create a new version)
  - Version auto-increment per prompt name
  - Diff output is non-empty for two different texts
  - AssertionResult scoring
  - EvalReport overall_score calculation
  - Regression detection: critical vs warning thresholds
  - Regression detection: no alert when score improves
  - At least 5 of 10 test cases pass with the mock parser
  - All EvalResults have score in [0.0, 1.0]
"""

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure src/ is on sys.path when running from repo root
_repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_repo_root / "src"))


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def isolated_registry(tmp_path):
    """PromptRegistry backed by a fresh in-memory SQLite DB."""
    import importlib

    import wanderwing.core.prompt_registry as reg_module

    # Patch engine to use isolated in-memory SQLite
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    tmp_db = f"sqlite:///{tmp_path / 'test_registry.db'}"
    engine = create_engine(tmp_db, connect_args={"check_same_thread": False})
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    reg_module._metadata.create_all(engine, checkfirst=True)

    with (
        patch.object(reg_module, "_engine", engine),
        patch.object(reg_module, "_SessionLocal", session_factory),
    ):
        yield reg_module.PromptRegistry()


@pytest.fixture
def isolated_runner(tmp_path):
    """EvalRunner backed by a fresh in-memory SQLite DB."""
    import wanderwing.core.eval_runner as runner_module

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    tmp_db = f"sqlite:///{tmp_path / 'test_runner.db'}"
    engine = create_engine(tmp_db, connect_args={"check_same_thread": False})
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    runner_module._metadata.create_all(engine, checkfirst=True)

    with (
        patch.object(runner_module, "_engine", engine),
        patch.object(runner_module, "_SessionLocal", session_factory),
    ):
        yield runner_module.EvalRunner()


@pytest.fixture
def mock_parser():
    from wanderwing.frontend.utils.mock_data import generate_parsed_intent
    return generate_parsed_intent


# ── Prompt Registry tests ─────────────────────────────────────────────────────


def test_hash_consistency(isolated_registry):
    """Same text always produces the same hash."""
    text = "You are an intent extractor.\nExtract destination and dates."
    v1 = isolated_registry.register("test_prompt", text)
    v2 = isolated_registry.register("test_prompt", text)
    assert v1.content_hash == v2.content_hash
    expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert v1.content_hash == expected_hash


def test_deduplication(isolated_registry):
    """Re-registering the same text returns the existing version (no new row)."""
    text = "Extract the destination from the user's message."
    v1 = isolated_registry.register("dedup_prompt", text)
    v2 = isolated_registry.register("dedup_prompt", text)
    assert v1.version_number == v2.version_number
    history = isolated_registry.get_history("dedup_prompt")
    assert len(history) == 1


def test_version_auto_increment(isolated_registry):
    """Version number increments with each distinct text registered."""
    v1 = isolated_registry.register("versioned", "Version one text.")
    v2 = isolated_registry.register("versioned", "Version two text — different.")
    v3 = isolated_registry.register("versioned", "Version three text — also different.")
    assert v1.version_number == 1
    assert v2.version_number == 2
    assert v3.version_number == 3


def test_version_numbers_independent_per_name(isolated_registry):
    """Version counters are scoped per prompt name."""
    a1 = isolated_registry.register("prompt_alpha", "Alpha v1")
    b1 = isolated_registry.register("prompt_beta", "Beta v1")
    a2 = isolated_registry.register("prompt_alpha", "Alpha v2")
    assert a1.version_number == 1
    assert b1.version_number == 1
    assert a2.version_number == 2


def test_diff_non_empty_for_different_texts(isolated_registry):
    """Diff between two different prompt texts is non-empty."""
    v1 = isolated_registry.register("diff_prompt", "Line one.\nLine two.\n")
    v2 = isolated_registry.register("diff_prompt", "Line one.\nLine two modified.\n")
    diff_str = isolated_registry.diff(v1.content_hash, v2.content_hash)
    assert len(diff_str) > 0
    assert "-Line two." in diff_str or "+Line two modified." in diff_str


def test_diff_empty_for_same_text(isolated_registry):
    """Diff between a version and itself is empty."""
    v = isolated_registry.register("same_prompt", "Identical text here.\n")
    diff_str = isolated_registry.diff(v.content_hash, v.content_hash)
    assert diff_str == ""


def test_get_current_returns_latest(isolated_registry):
    """get_current always returns the highest version number."""
    isolated_registry.register("current_test", "First version")
    isolated_registry.register("current_test", "Second version")
    v3 = isolated_registry.register("current_test", "Third version")
    current = isolated_registry.get_current("current_test")
    assert current is not None
    assert current.version_number == v3.version_number


def test_get_current_returns_none_for_unknown(isolated_registry):
    """get_current returns None for a prompt name that was never registered."""
    result = isolated_registry.get_current("does_not_exist")
    assert result is None


def test_register_from_files(isolated_registry, tmp_path):
    """register_from_files scans .txt files and registers each one."""
    (tmp_path / "prompt_a.txt").write_text("Prompt A content.")
    (tmp_path / "prompt_b.txt").write_text("Prompt B content.")
    (tmp_path / "not_a_prompt.json").write_text("{}")  # should be ignored

    versions = isolated_registry.register_from_files(str(tmp_path))
    names = [v.name for v in versions]
    assert "prompt_a" in names
    assert "prompt_b" in names
    assert "not_a_prompt" not in names


# ── Eval framework data type tests ────────────────────────────────────────────


def test_assertion_result_scoring():
    """AssertionResult score is 1.0 when passed, 0.0 when failed."""
    from wanderwing.core.eval_runner import AssertionResult

    passing = AssertionResult(name="check_dest", passed=True, score=1.0, reason="ok")
    failing = AssertionResult(name="check_dest", passed=False, score=0.0, reason="no")
    assert passing.score == 1.0
    assert failing.score == 0.0


def test_eval_report_overall_score_calculation(isolated_runner, mock_parser):
    """overall_score is the mean of per-test-case scores."""
    report = isolated_runner.run("intent_extraction", mock_parser)
    if report.total == 0:
        pytest.skip("No test cases")
    expected = sum(r.score for r in report.results) / report.total
    assert abs(report.overall_score - round(expected, 4)) < 1e-6


def test_all_eval_results_scores_in_range(isolated_runner, mock_parser):
    """Every EvalResult score is in [0.0, 1.0]."""
    report = isolated_runner.run("intent_extraction", mock_parser)
    for r in report.results:
        assert 0.0 <= r.score <= 1.0, f"{r.test_case_id} score out of range: {r.score}"


# ── Regression detection tests ────────────────────────────────────────────────


def test_regression_detection_no_previous(isolated_runner):
    """No alerts when there is no previous report."""
    from wanderwing.core.eval_runner import EvalReport, EvalResult

    current = EvalReport(
        prompt_name="p",
        prompt_hash="abc",
        total=1,
        passed=1,
        overall_score=1.0,
        results=[
            EvalResult(
                test_case_id="TC01",
                test_case_name="test",
                prompt_hash="abc",
                score=1.0,
                passed=True,
            )
        ],
    )
    alerts = isolated_runner.detect_regressions(current, previous=None)
    assert alerts == []


def test_regression_detection_critical(isolated_runner):
    """A score drop >= 0.20 triggers a critical alert."""
    from wanderwing.core.eval_runner import EvalReport, EvalResult

    def _report(score):
        return EvalReport(
            prompt_name="p",
            prompt_hash="h",
            total=1,
            passed=1 if score >= 0.75 else 0,
            overall_score=score,
            results=[
                EvalResult(
                    test_case_id="TC01",
                    test_case_name="Tokyo hiking",
                    prompt_hash="h",
                    score=score,
                    passed=score >= 0.75,
                )
            ],
        )

    previous = _report(1.0)
    current = _report(0.0)  # drop of 1.0 → critical
    alerts = isolated_runner.detect_regressions(current, previous)
    assert len(alerts) == 1
    assert alerts[0].severity == "critical"
    assert alerts[0].delta == pytest.approx(-1.0)


def test_regression_detection_warning(isolated_runner):
    """A score drop between 0.05 and 0.20 triggers a warning alert."""
    from wanderwing.core.eval_runner import EvalReport, EvalResult

    def _report(score):
        return EvalReport(
            prompt_name="p",
            prompt_hash="h",
            total=1,
            passed=1,
            overall_score=score,
            results=[
                EvalResult(
                    test_case_id="TC02",
                    test_case_name="Paris museums",
                    prompt_hash="h",
                    score=score,
                    passed=True,
                )
            ],
        )

    previous = _report(1.0)
    current = _report(0.88)  # drop of 0.12 → warning (between 0.05 and 0.20)
    alerts = isolated_runner.detect_regressions(current, previous)
    assert len(alerts) == 1
    assert alerts[0].severity == "warning"


def test_regression_detection_no_alert_on_improvement(isolated_runner):
    """No alert when score improves."""
    from wanderwing.core.eval_runner import EvalReport, EvalResult

    def _report(score):
        return EvalReport(
            prompt_name="p",
            prompt_hash="h",
            total=1,
            passed=1,
            overall_score=score,
            results=[
                EvalResult(
                    test_case_id="TC03",
                    test_case_name="Barcelona beach",
                    prompt_hash="h",
                    score=score,
                    passed=True,
                )
            ],
        )

    previous = _report(0.5)
    current = _report(1.0)  # improvement
    alerts = isolated_runner.detect_regressions(current, previous)
    assert alerts == []


def test_regression_no_alert_below_warn_threshold(isolated_runner):
    """A drop smaller than warn_threshold (0.05) does not generate an alert."""
    from wanderwing.core.eval_runner import EvalReport, EvalResult

    def _report(score):
        return EvalReport(
            prompt_name="p",
            prompt_hash="h",
            total=1,
            passed=1,
            overall_score=score,
            results=[
                EvalResult(
                    test_case_id="TC04",
                    test_case_name="London nightlife",
                    prompt_hash="h",
                    score=score,
                    passed=True,
                )
            ],
        )

    previous = _report(1.0)
    current = _report(0.97)  # drop of 0.03 < 0.05 threshold
    alerts = isolated_runner.detect_regressions(current, previous)
    assert alerts == []


# ── Mock parser integration tests ─────────────────────────────────────────────


def test_at_least_5_test_cases_pass_with_mock(isolated_runner, mock_parser):
    """At least 5 of the 10 test cases pass with the mock parser."""
    report = isolated_runner.run("intent_extraction", mock_parser)
    assert report.passed >= 5, (
        f"Expected at least 5 passing test cases with mock parser, "
        f"got {report.passed}/{report.total}. "
        f"Scores: {[(r.test_case_id, r.score) for r in report.results]}"
    )


def test_store_and_load_report(isolated_runner, mock_parser):
    """Storing a report and loading it back returns the same data."""
    report = isolated_runner.run("intent_extraction", mock_parser)
    isolated_runner.store_report(report)
    loaded = isolated_runner.load_previous_report("intent_extraction")

    assert loaded is not None
    assert loaded.prompt_name == report.prompt_name
    assert loaded.total == report.total
    assert loaded.passed == report.passed
    assert abs(loaded.overall_score - report.overall_score) < 1e-5
    assert len(loaded.results) == len(report.results)
