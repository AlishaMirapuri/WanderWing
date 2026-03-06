"""Experiment Dashboard — live metrics from DB (falls back to mock data if empty)."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_skeleton_card, render_empty_state
from wanderwing.frontend.utils.mock_data import (
    generate_acceptance_rate_by_day,
    generate_parse_success_over_time,
)
from wanderwing.frontend.components.charts import (
    render_acceptance_rate_chart,
    render_parse_success_chart,
    render_metrics_grid,
)


def _load_live_metrics() -> list[dict] | None:
    """Try API first, fall back to direct DB query, return None if no data."""
    try:
        import httpx
        resp = httpx.get("http://localhost:8000/experiments/summary", timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            if any(m.get("user_count", 0) > 0 for m in data):
                return data
    except Exception:
        pass

    try:
        from wanderwing.core.event_logger import event_logger
        metrics = event_logger.compute_metrics()
        return [m.to_dict() for m in metrics.values()]
    except Exception:
        return None


def _render_variant_metrics_table(metrics_list: list[dict]) -> None:
    import pandas as pd

    rows = []
    for m in metrics_list:
        rows.append({
            "Variant": m["variant"].replace("_", " ").title(),
            "Users": m["user_count"],
            "Completion": f"{m['completion_rate'] * 100:.1f}%",
            "Match CTR": f"{m['match_clickthrough_rate'] * 100:.1f}%",
            "Rec. satisfaction": f"{m['recommendation_satisfaction']:.2f}",
            "Parse correction": f"{m['parse_correction_rate'] * 100:.1f}%",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_funnel_chart(metrics_list: list[dict]) -> None:
    try:
        import pandas as pd
        import altair as alt

        event_order = [
            "profile_completed",
            "parse_accepted",
            "match_clicked",
            "recommendation_liked",
            "feedback_submitted",
        ]

        rows = []
        for m in metrics_list:
            funnel = m.get("funnel", {})
            variant_label = m["variant"].replace("_", " ").title()
            for et in event_order:
                rows.append({
                    "Variant": variant_label,
                    "Event": et.replace("_", " ").title(),
                    "Count": funnel.get(et, 0),
                })

        df = pd.DataFrame(rows)
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("Variant:N", title="Variant"),
                y=alt.Y("Count:Q", title="Event Count"),
                color=alt.Color("Event:N", sort=event_order),
                tooltip=["Variant", "Event", "Count"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)
    except ImportError:
        import pandas as pd
        rows = []
        for m in metrics_list:
            funnel = m.get("funnel", {})
            row = {"Variant": m["variant"].replace("_", " ").title()}
            row.update(funnel)
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render():
    """Render the Experiment Dashboard page."""
    render_page_header(
        "Experiment dashboard.",
        "Live A/B/C test metrics from the event store.",
    )

    metrics_list = _load_live_metrics()
    has_data = metrics_list and any(m.get("user_count", 0) > 0 for m in metrics_list)

    if not has_data:
        st.warning(
            "No experiment data yet. Run `python3 scripts/generate_synthetic_data.py` "
            "to seed the database, or navigate through the app to generate real events."
        )

    # ── Key metrics ───────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:1.5rem 0 0.75rem;">Key metrics by variant</div>',
        unsafe_allow_html=True,
    )

    if has_data:
        _render_variant_metrics_table(metrics_list)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        cols = st.columns(len(metrics_list))
        for col, m in zip(cols, metrics_list):
            label = m["variant"].replace("_", " ").title()
            with col:
                st.metric(label=f"{label} \u2014 Completion", value=f"{m['completion_rate'] * 100:.1f}%")
                st.metric(label="Match CTR", value=f"{m['match_clickthrough_rate'] * 100:.1f}%")
                st.metric(label="Rec. satisfaction", value=f"{m['recommendation_satisfaction']:.2f}")
                st.metric(label="Parse correction", value=f"{m['parse_correction_rate'] * 100:.1f}%")
    else:
        # Skeleton metric placeholders — shimmer until real data arrives
        skel_cols = st.columns(3)
        for col in skel_cols:
            with col:
                render_skeleton_card(lines=4)

    # ── Funnel ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:2rem 0 0.4rem;">Event funnel by variant</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.82rem;color:rgba(26,26,46,0.45);margin-bottom:0.75rem;">'
        'Raw event counts at each workflow step. Steeper drop = more users abandoning at that step.</p>',
        unsafe_allow_html=True,
    )

    if has_data:
        _render_funnel_chart(metrics_list)
    else:
        render_empty_state(
            "No funnel data yet.",
            "Run scripts/generate_synthetic_data.py or navigate through the app to generate events.",
        )

    # ── Historical charts ─────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:2rem 0 0.4rem;">Match acceptance (last 30 days)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.78rem;color:rgba(26,26,46,0.40);margin-bottom:0.5rem;">'
        'Synthetic data shown for illustration.</p>',
        unsafe_allow_html=True,
    )
    render_acceptance_rate_chart(generate_acceptance_rate_by_day(days=30))

    st.markdown(
        '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:2rem 0 0.4rem;">Parse success (last 12 weeks)</div>',
        unsafe_allow_html=True,
    )
    render_parse_success_chart(generate_parse_success_over_time(weeks=12))

    # ── Raw data ──────────────────────────────────────────────────────────────
    if has_data:
        with st.expander("Raw metrics JSON"):
            import json
            st.json(metrics_list)

    # ── Config ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:2rem 0 1rem;">Experiment configuration</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ww-card ww-anim">'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;">'
        '<div>'
        '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.09em;color:rgba(26,26,46,0.32);margin-bottom:0.6rem;">Traffic split</div>'
        '<div style="font-size:0.88rem;color:rgba(26,26,46,0.65);line-height:1.8;">'
        'Variant A \u2014 Structured Preview: <strong style="color:#1A1A2E;">40%</strong><br>'
        'Variant B \u2014 Fast to Matches: <strong style="color:#1A1A2E;">40%</strong><br>'
        'Variant C \u2014 Explainable: <strong style="color:#1A1A2E;">20%</strong>'
        '</div>'
        '</div>'
        '<div>'
        '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.09em;color:rgba(26,26,46,0.32);margin-bottom:0.6rem;">Success criteria</div>'
        '<div style="font-size:0.88rem;color:rgba(26,26,46,0.65);line-height:1.8;">'
        'Completion rate &gt; 50%<br>'
        'Match CTR &gt; 70%<br>'
        'Rec. satisfaction &gt; 0.60<br>'
        'Parse correction &lt; 15%'
        '</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("experiment_variant"):
        variant = st.session_state.experiment_variant
        st.markdown(
            f'<p style="font-size:0.78rem;color:rgba(26,26,46,0.45);margin-top:0.75rem;">'
            f'Your session: <code style="background:rgba(26,26,46,0.06);padding:0.1rem 0.4rem;'
            f'border-radius:4px;font-size:0.75rem;">{variant}</code> '
            f'(assigned deterministically from session ID)</p>',
            unsafe_allow_html=True,
        )
