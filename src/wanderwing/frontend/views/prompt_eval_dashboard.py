"""
Prompt Eval Dashboard — Streamlit page.

4 tabs:
  1. Version History  — registered prompt versions
  2. Prompt Diff      — colored unified diff between two versions
  3. Eval Results     — latest eval report per test case
  4. Regression Alerts — comparison vs previous run
"""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header


# ── Helpers ───────────────────────────────────────────────────────────────────


def _load_registry():
    try:
        from wanderwing.core.prompt_registry import prompt_registry
        return prompt_registry
    except Exception:
        return None


def _load_runner():
    try:
        from wanderwing.core.eval_runner import EvalRunner
        return EvalRunner()
    except Exception:
        return None


def _diff_to_html(diff_text: str) -> str:
    """Convert unified diff text to styled HTML."""
    if not diff_text:
        return (
            '<p style="color:rgba(26,26,46,0.40);font-style:italic;'
            'font-size:0.88rem;">No differences found.</p>'
        )

    lines_html = []
    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            style = "color:#1A1A2E;font-weight:600;"
        elif line.startswith("+"):
            style = "background:rgba(255,107,107,0.10);color:#FF6B6B;"
        elif line.startswith("-"):
            style = "background:rgba(26,26,46,0.05);color:rgba(26,26,46,0.50);text-decoration:line-through;"
        elif line.startswith("@@"):
            style = "color:rgba(26,26,46,0.40);font-weight:600;"
        else:
            style = "color:rgba(26,26,46,0.65);"
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines_html.append(
            f'<div style="{style}font-family:monospace;font-size:0.82rem;'
            f'white-space:pre;padding:0.05rem 0.5rem;">{escaped}</div>'
        )

    return (
        '<div style="border:1px solid rgba(255,107,107,0.12);border-radius:16px;'
        'padding:1rem;background:#FFFFFF;overflow-x:auto;">'
        + "\n".join(lines_html)
        + "</div>"
    )


def _severity_badge(severity: str) -> str:
    if severity == "critical":
        return (
            '<span style="background:rgba(255,107,107,0.15);color:#FF6B6B;'
            'padding:0.15rem 0.55rem;border-radius:100px;font-size:0.75rem;'
            'font-weight:600;">Critical</span>'
        )
    return (
        '<span style="background:rgba(26,26,46,0.07);color:rgba(26,26,46,0.55);'
        'padding:0.15rem 0.55rem;border-radius:100px;font-size:0.75rem;'
        'font-weight:600;">Warning</span>'
    )


# ── Tab renderers ─────────────────────────────────────────────────────────────


def _render_version_history(registry) -> None:
    st.markdown(
        '<p style="font-size:0.88rem;color:rgba(26,26,46,0.55);margin-bottom:1.25rem;">'
        'All prompt versions indexed by SHA256 hash. Re-registering the same text '
        'returns the existing entry (deduplication).</p>',
        unsafe_allow_html=True,
    )

    if registry is None:
        st.error("Could not load PromptRegistry.")
        return

    versions = registry.list_all()
    if not versions:
        st.markdown(
            '<p style="font-size:0.88rem;color:rgba(26,26,46,0.45);">'
            'No prompt versions yet. Run <code>python3 scripts/run_prompt_evals.py --register</code> '
            'to scan prompt files.</p>',
            unsafe_allow_html=True,
        )
        return

    try:
        import pandas as pd

        rows = [
            {
                "Prompt": v.name,
                "Version": f"v{v.version_number}",
                "Hash": v.hash_prefix,
                "Lines": v.line_count,
                "Registered": str(v.registered_at)[:19] if v.registered_at else "\u2014",
            }
            for v in versions
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except ImportError:
        for v in versions:
            st.markdown(
                f"**{v.name}** v{v.version_number} · `{v.hash_prefix}` · "
                f"{v.line_count} lines · {str(v.registered_at)[:19]}"
            )


def _render_prompt_diff(registry) -> None:
    st.markdown(
        '<p style="font-size:0.88rem;color:rgba(26,26,46,0.55);margin-bottom:1.25rem;">'
        'Select two versions to compare. Additions are highlighted in red, deletions struck through.</p>',
        unsafe_allow_html=True,
    )

    if registry is None:
        st.error("Could not load PromptRegistry.")
        return

    versions = registry.list_all()
    if len(versions) < 1:
        st.markdown(
            '<p style="font-size:0.88rem;color:rgba(26,26,46,0.45);">'
            'Register at least one prompt version first.</p>',
            unsafe_allow_html=True,
        )
        return

    version_labels = [f"{v.name} v{v.version_number} ({v.hash_prefix})" for v in versions]
    hash_map = {
        f"{v.name} v{v.version_number} ({v.hash_prefix})": v.content_hash
        for v in versions
    }

    col1, col2 = st.columns(2)
    with col1:
        label_a = st.selectbox("Version A (from)", version_labels, key="diff_a")
    with col2:
        label_b = st.selectbox(
            "Version B (to)",
            version_labels,
            index=min(1, len(version_labels) - 1),
            key="diff_b",
        )

    if st.button("Show diff", type="primary"):
        hash_a = hash_map.get(label_a, "")
        hash_b = hash_map.get(label_b, "")
        diff_text = registry.diff(hash_a, hash_b)
        st.markdown(_diff_to_html(diff_text), unsafe_allow_html=True)


def _render_eval_results(runner) -> None:
    st.markdown(
        '<p style="font-size:0.88rem;color:rgba(26,26,46,0.55);margin-bottom:1.25rem;">'
        'Most recent eval run for <code>intent_extraction</code>. '
        'Run <code>python3 scripts/run_prompt_evals.py</code> to refresh.</p>',
        unsafe_allow_html=True,
    )

    if runner is None:
        st.error("Could not load EvalRunner.")
        return

    report = runner.load_previous_report("intent_extraction")
    if report is None:
        st.markdown(
            '<p style="font-size:0.88rem;color:rgba(26,26,46,0.45);">'
            'No eval reports yet. Run <code>python3 scripts/run_prompt_evals.py</code> to generate one.</p>',
            unsafe_allow_html=True,
        )
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", report.total)
    col2.metric("Passed", report.passed)
    col3.metric("Failed", report.total - report.passed)
    col4.metric("Score", f"{report.overall_score:.1%}")

    st.markdown(
        f'<p style="font-size:0.75rem;color:rgba(26,26,46,0.35);margin:0.5rem 0 1rem;">'
        f'Run at {str(report.run_at)[:19]} \u00b7 hash <code>{report.prompt_hash[:8]}</code></p>',
        unsafe_allow_html=True,
    )

    try:
        import pandas as pd

        rows = []
        for r in report.results:
            status = "Pass" if r.passed else "Fail"
            assertion_summary = "; ".join(
                f"{'✓' if a.passed else '✗'} {a.name}" for a in r.assertion_results
            )
            rows.append({
                "ID": r.test_case_id,
                "Test case": r.test_case_name,
                "Score": f"{r.score:.2f}",
                "Status": status,
                "Assertions": assertion_summary,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except ImportError:
        for r in report.results:
            icon = "✅" if r.passed else "❌"
            st.markdown(f"{icon} **{r.test_case_id}** {r.test_case_name} — {r.score:.2f}")

    with st.expander("Assertion details"):
        for r in report.results:
            st.markdown(f"**{r.test_case_id} \u2014 {r.test_case_name}** (score: {r.score:.2f})")
            for a in r.assertion_results:
                icon = "✅" if a.passed else "❌"
                st.markdown(f"&nbsp;&nbsp;{icon} `{a.name}` \u2014 {a.reason}")
            st.markdown("---")


def _render_regression_alerts(runner) -> None:
    st.markdown(
        '<p style="font-size:0.88rem;color:rgba(26,26,46,0.55);margin-bottom:1.25rem;">'
        'Score drops vs the previous eval run. '
        'Critical = drop \u2265 0.20 \u00b7 Warning = drop \u2265 0.05.</p>',
        unsafe_allow_html=True,
    )

    if runner is None:
        st.error("Could not load EvalRunner.")
        return

    all_reports = runner.load_all_reports("intent_extraction")
    if len(all_reports) < 2:
        st.markdown(
            '<p style="font-size:0.88rem;color:rgba(26,26,46,0.45);">'
            'Need at least 2 eval runs to detect regressions. '
            'Run <code>python3 scripts/run_prompt_evals.py</code> twice.</p>',
            unsafe_allow_html=True,
        )
        if len(all_reports) == 1:
            st.success(
                f"1 report found (score: {all_reports[0].overall_score:.1%}). "
                "Run again after editing a prompt to see regressions."
            )
        return

    current = all_reports[0]
    previous = all_reports[1]
    alerts = runner.detect_regressions(current, previous)

    col1, col2 = st.columns(2)
    col1.metric("Previous score", f"{previous.overall_score:.1%}")
    col2.metric(
        "Current score",
        f"{current.overall_score:.1%}",
        delta=f"{(current.overall_score - previous.overall_score):+.1%}",
    )

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    if not alerts:
        st.success("No regressions detected — all test cases held or improved.")
        return

    critical = [a for a in alerts if a.severity == "critical"]
    warnings_list = [a for a in alerts if a.severity == "warning"]

    if critical:
        st.error(f"{len(critical)} critical regression(s) detected.")
    if warnings_list:
        st.warning(f"{len(warnings_list)} warning(s) detected.")

    try:
        import pandas as pd

        rows = [
            {
                "Severity": a.severity.title(),
                "ID": a.test_case_id,
                "Test case": a.test_case_name,
                "Previous": f"{a.previous_score:.2f}",
                "Current": f"{a.current_score:.2f}",
                "Delta": f"{a.delta:+.2f}",
            }
            for a in alerts
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except ImportError:
        for a in alerts:
            st.markdown(
                f"**{a.severity.title()}** {a.test_case_id} {a.test_case_name} "
                f"\u2014 {a.previous_score:.2f} \u2192 {a.current_score:.2f} (\u0394 {a.delta:+.2f})"
            )


# ── Main render ───────────────────────────────────────────────────────────────


def render() -> None:
    render_page_header(
        "Prompt registry.",
        "Version tracking, unified diffs, and eval regression detection.",
    )

    registry = _load_registry()
    runner = _load_runner()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Version history", "Prompt diff", "Eval results", "Regression alerts"]
    )

    with tab1:
        _render_version_history(registry)

    with tab2:
        _render_prompt_diff(registry)

    with tab3:
        _render_eval_results(runner)

    with tab4:
        _render_regression_alerts(runner)
