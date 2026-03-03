"""
Chart components for experiment dashboard.

Provides visualizations for metrics and experiment results.
"""

import streamlit as st
import pandas as pd


def render_acceptance_rate_chart(data):
    """
    Render line chart for match acceptance rate over time.

    Args:
        data: List of dicts with 'date' and 'acceptance_rate' keys
    """
    df = pd.DataFrame(data)
    df['acceptance_rate_pct'] = df['acceptance_rate'] * 100

    st.line_chart(
        df,
        x='date',
        y='acceptance_rate_pct',
        use_container_width=True,
    )


def render_feedback_by_variant_chart(data):
    """
    Render bar chart for average feedback score by UX variant.

    Args:
        data: List of dicts with 'variant', 'avg_score', 'count' keys
    """
    df = pd.DataFrame(data)

    st.bar_chart(
        df,
        x='variant',
        y='avg_score',
        use_container_width=True,
    )

    # Show counts in table
    st.markdown("##### Sample Sizes")
    st.dataframe(
        df[['variant', 'count']],
        use_container_width=True,
        hide_index=True,
    )


def render_parse_success_chart(data):
    """
    Render area chart for parse success rate over time.

    Args:
        data: List of dicts with 'week' and 'success_rate' keys
    """
    df = pd.DataFrame(data)
    df['success_rate_pct'] = df['success_rate'] * 100

    st.area_chart(
        df,
        x='week',
        y='success_rate_pct',
        use_container_width=True,
        color="#10B981",
    )


def render_metrics_grid(metrics):
    """
    Render grid of key metrics.

    Args:
        metrics: Dict with metric name -> value pairs
    """
    cols = st.columns(len(metrics))

    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.markdown(
                f"""
                <div style="background: white; border-radius: 12px; padding: 1.5rem;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1E3A8A;">
                        {value}
                    </div>
                    <div style="font-size: 0.95rem; color: #6B7280; margin-top: 0.5rem;">
                        {label}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
