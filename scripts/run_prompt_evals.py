#!/usr/bin/env python3
"""
CLI runner for WanderWing prompt version registration and eval regression checks.

Usage:
    python3 scripts/run_prompt_evals.py                     # run all evals, print report
    python3 scripts/run_prompt_evals.py --register          # scan agents/prompts/*.txt and register
    python3 scripts/run_prompt_evals.py --check-regressions # exit 1 if critical regression (CI mode)
    python3 scripts/run_prompt_evals.py --diff <hash_a> <hash_b>   # show prompt diff
"""

import argparse
import sys
from pathlib import Path

# Ensure the src directory is on the Python path when running from repo root
_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))


def _get_parser_fn():
    """Return generate_parsed_intent (mock). Falls back gracefully."""
    from wanderwing.frontend.utils.mock_data import generate_parsed_intent
    return generate_parsed_intent


def _get_prompt_hash(registry, prompt_name: str) -> str:
    """Return the current prompt hash, or 'mock' if not registered."""
    version = registry.get_current(prompt_name)
    return version.content_hash if version else "mock"


def cmd_register(prompts_dir: str) -> None:
    from wanderwing.core.prompt_registry import prompt_registry

    print(f"Scanning {prompts_dir} for *.txt prompt files...")
    versions = prompt_registry.register_from_files(prompts_dir)
    if not versions:
        print("No .txt prompt files found.")
        return

    for v in versions:
        print(
            f"  {'[new]' if v.version_number > 1 else '[v1]':6s} "
            f"{v.name:40s} v{v.version_number}  {v.hash_prefix}  ({v.line_count} lines)"
        )
    print(f"\nRegistered {len(versions)} prompt(s).")


def cmd_run(check_regressions: bool = False) -> None:
    from wanderwing.core.eval_runner import EvalRunner
    from wanderwing.core.prompt_registry import prompt_registry

    runner = EvalRunner()
    parser_fn = _get_parser_fn()

    prompt_name = "intent_extraction"
    prompt_hash = _get_prompt_hash(prompt_registry, prompt_name)

    print(f"Running evals for '{prompt_name}' (hash: {prompt_hash[:8]})")
    print("=" * 60)

    # Load previous report BEFORE storing the current one
    previous = runner.load_previous_report(prompt_name)

    report = runner.run(prompt_name, parser_fn, prompt_hash=prompt_hash)

    # Print per-test-case results
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        mark = "✓" if r.passed else "✗"
        print(f"  {mark} [{status}] {r.test_case_id}: {r.test_case_name:<35s} score={r.score:.2f}")
        for a in r.assertion_results:
            icon = "  ✓" if a.passed else "  ✗"
            print(f"         {icon} {a.name}: {a.reason}")

    print()
    print(f"Result: {report.passed}/{report.total} passed  |  overall score: {report.overall_score:.2%}")
    print(f"Run at: {str(report.run_at)[:19]}")

    # Regression check
    alerts = runner.detect_regressions(report, previous)
    if alerts:
        print()
        print("⚠️  Regression Alerts:")
        has_critical = False
        for a in alerts:
            severity_label = "CRITICAL" if a.severity == "critical" else "WARNING "
            print(
                f"  [{severity_label}] {a.test_case_id} {a.test_case_name}: "
                f"{a.previous_score:.2f} → {a.current_score:.2f}  (Δ {a.delta:+.2f})"
            )
            if a.severity == "critical":
                has_critical = True
    elif previous is not None:
        print()
        print("✅ No regressions detected vs previous run.")
    else:
        print()
        print("ℹ️  No previous run to compare against (first run).")

    # Persist after printing so load_previous_report next run sees this one
    runner.store_report(report)
    print(f"\nReport stored to DB.")

    if check_regressions and alerts:
        critical_alerts = [a for a in alerts if a.severity == "critical"]
        if critical_alerts:
            print(f"\n❌ CI GATE FAILED: {len(critical_alerts)} critical regression(s). Exiting 1.")
            sys.exit(1)
        else:
            print(f"\n⚠️  CI: {len(alerts)} warning(s) only — exit 0.")


def cmd_diff(hash_a: str, hash_b: str) -> None:
    from wanderwing.core.prompt_registry import prompt_registry

    diff_text = prompt_registry.diff(hash_a, hash_b)
    if not diff_text:
        print("No differences found (or one/both hashes not registered).")
    else:
        print(diff_text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WanderWing Prompt Eval CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--register",
        action="store_true",
        help="Scan agents/prompts/*.txt and register versions in the DB",
    )
    parser.add_argument(
        "--check-regressions",
        action="store_true",
        help="Exit 1 if a critical regression is detected (CI mode)",
    )
    parser.add_argument(
        "--diff",
        nargs=2,
        metavar=("HASH_A", "HASH_B"),
        help="Print unified diff between two prompt versions",
    )
    parser.add_argument(
        "--prompts-dir",
        default=str(_repo_root / "src" / "wanderwing" / "agents" / "prompts"),
        help="Directory to scan for .txt prompt files (used with --register)",
    )

    args = parser.parse_args()

    if args.diff:
        cmd_diff(args.diff[0], args.diff[1])
    elif args.register:
        cmd_register(args.prompts_dir)
    else:
        cmd_run(check_regressions=args.check_regressions)


if __name__ == "__main__":
    main()
