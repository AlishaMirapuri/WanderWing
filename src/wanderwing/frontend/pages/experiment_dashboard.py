"""Experiment Dashboard page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header
from wanderwing.frontend.utils.mock_data import (
    generate_dashboard_metrics,
    generate_acceptance_rate_by_day,
    generate_feedback_by_variant,
    generate_parse_success_over_time,
)
from wanderwing.frontend.components.charts import (
    render_acceptance_rate_chart,
    render_feedback_by_variant_chart,
    render_parse_success_chart,
    render_metrics_grid,
)


def render():
    """Render the Experiment Dashboard page."""
    render_page_header(
        "Experiment Dashboard",
        "Track key metrics and A/B test results"
    )

    # Generate mock data
    metrics = generate_dashboard_metrics()
    acceptance_data = generate_acceptance_rate_by_day(days=30)
    feedback_data = generate_feedback_by_variant()
    parse_data = generate_parse_success_over_time(weeks=12)

    # Key Metrics
    st.markdown("### Key Metrics")

    render_metrics_grid({
        "Total Matches": f"{metrics['total_matches']}",
        "Acceptance Rate": f"{int(metrics['match_acceptance_rate'] * 100)}%",
        "Avg Rating": f"{metrics['avg_feedback_score']} ⭐",
        "Parse Success": f"{int(metrics['parse_success_rate'] * 100)}%",
    })

    st.markdown("---")

    # Match Acceptance Rate Over Time
    st.markdown("### Match Acceptance Rate (Last 30 Days)")
    st.markdown(
        """
        Tracks the percentage of matches that users accepted and connected with over time.
        Higher is better - indicates quality matches.
        """
    )

    render_acceptance_rate_chart(acceptance_data)

    st.markdown("---")

    # Feedback Score by UX Variant
    st.markdown("### Average Feedback Score by UX Variant")
    st.markdown(
        """
        A/B test results comparing different UX designs.
        Measures user satisfaction with the matching experience.
        """
    )

    render_feedback_by_variant_chart(feedback_data)

    # Insights
    col1, col2 = st.columns(2)

    with col1:
        st.success(
            """
            ✅ **Variant B performing best** with 4.5 avg rating (+0.3 vs Variant A)
            """
        )

    with col2:
        st.info(
            """
            📊 **Sample size** for Variant B is sufficient for statistical significance
            """
        )

    st.markdown("---")

    # Parse Success Rate Over Time
    st.markdown("### Intent Parse Success Rate (Last 12 Weeks)")
    st.markdown(
        """
        Tracks how reliably the AI extracts structured trip information from user descriptions.
        Shows improvement as the model learns from feedback.
        """
    )

    render_parse_success_chart(parse_data)

    st.info(
        """
        📈 **Trending upward:** Parse success has improved 8% over the last 12 weeks
        thanks to continuous model refinement.
        """
    )

    st.markdown("---")

    # Detailed Metrics Table
    st.markdown("### Detailed Metrics")

    with st.expander("View Raw Data"):
        import pandas as pd

        # Recent acceptance rates
        st.markdown("#### Recent Acceptance Rates")
        df_acceptance = pd.DataFrame(acceptance_data[-7:])  # Last 7 days
        st.dataframe(df_acceptance, use_container_width=True, hide_index=True)

        st.markdown("#### Variant Performance")
        df_variants = pd.DataFrame(feedback_data)
        st.dataframe(df_variants, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.markdown("### Experiment Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            **Active Experiments:**
            - UX Variant Testing (3 variants)
            - Parse Model v2 vs v3
            - Activity Recommendation Algo A/B

            **Traffic Split:**
            - Variant A: 40%
            - Variant B: 40%
            - Variant C: 20%
            """
        )

    with col2:
        st.markdown(
            """
            **Success Criteria:**
            - Acceptance rate > 65%
            - Avg feedback score > 4.0
            - Parse success > 90%

            **Current Status:**
            - ✅ Acceptance: 68% (target: 65%)
            - ✅ Feedback: 4.3 (target: 4.0)
            - ⚠️ Parse: 89% (target: 90%)
            """
        )
