"""
Styling utilities for WanderWing Streamlit frontend.

Provides consistent styling, CSS, and theme configuration.
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS for modern, polished UI."""
    st.markdown(
        """
        <style>
        /* Main layout */
        .main {
            padding: 2rem;
        }

        /* Headers */
        h1 {
            color: #1E3A8A;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        h2 {
            color: #2563EB;
            font-weight: 600;
            margin-top: 2rem;
        }

        h3 {
            color: #3B82F6;
            font-weight: 600;
        }

        /* Cards */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border: 1px solid #E5E7EB;
        }

        .card-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 0.75rem;
        }

        .card-subheader {
            font-size: 0.95rem;
            color: #6B7280;
            margin-bottom: 1rem;
        }

        /* Match cards */
        .match-card {
            background: linear-gradient(135deg, #EEF2FF 0%, #DBEAFE 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 2px solid #3B82F6;
        }

        .match-score {
            font-size: 2rem;
            font-weight: 700;
            color: #2563EB;
        }

        /* Activity cards */
        .activity-card {
            background: white;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid #E5E7EB;
            transition: transform 0.2s;
        }

        .activity-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* Tags */
        .tag {
            display: inline-block;
            background: #DBEAFE;
            color: #1E40AF;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .tag-success {
            background: #D1FAE5;
            color: #065F46;
        }

        .tag-warning {
            background: #FEF3C7;
            color: #92400E;
        }

        .tag-info {
            background: #E0E7FF;
            color: #3730A3;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
        }

        .badge-high {
            background: #DEF7EC;
            color: #03543F;
        }

        .badge-medium {
            background: #FEF3C7;
            color: #92400E;
        }

        .badge-low {
            background: #FEE2E2;
            color: #991B1B;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            border: none;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* Forms */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            border-radius: 8px;
            border: 1px solid #D1D5DB;
        }

        /* Metrics */
        .metric-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E3A8A;
        }

        .metric-label {
            font-size: 0.95rem;
            color: #6B7280;
            margin-top: 0.5rem;
        }

        /* Success/Info boxes */
        .success-box {
            background: #DEF7EC;
            border-left: 4px solid #10B981;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        .info-box {
            background: #EEF2FF;
            border-left: 4px solid #3B82F6;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        .warning-box {
            background: #FEF3C7;
            border-left: 4px solid #F59E0B;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        /* Sidebar */
        .css-1d391kg {
            background: #F9FAFB;
        }

        /* Progress */
        .stProgress > div > div > div {
            background: #3B82F6;
        }

        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #E5E7EB;
        }

        /* Code blocks for parsed intent */
        .stCodeBlock {
            border-radius: 8px;
        }

        /* Comparison view */
        .comparison-container {
            display: flex;
            gap: 1rem;
        }

        .comparison-column {
            flex: 1;
            background: #F9FAFB;
            padding: 1rem;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str = ""):
    """Render consistent page header."""
    st.markdown(f"# 🌍 {title}")
    if subtitle:
        st.markdown(f"<p style='color: #6B7280; font-size: 1.1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def render_card(title: str, content: str, card_type: str = "default"):
    """Render a styled card."""
    if card_type == "match":
        st.markdown(
            f"""
            <div class="match-card">
                <div class="card-header">{title}</div>
                <div>{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-header">{title}</div>
                <div>{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_tag(text: str, tag_type: str = "default"):
    """Render a styled tag."""
    tag_class = f"tag tag-{tag_type}" if tag_type != "default" else "tag"
    return f'<span class="{tag_class}">{text}</span>'


def render_badge(text: str, badge_type: str = "high"):
    """Render a styled badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def render_metric_card(value: str, label: str):
    """Render a metric card."""
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_success_message(message: str):
    """Render a success message box."""
    st.markdown(
        f"""
        <div class="success-box">
            ✅ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_message(message: str):
    """Render an info message box."""
    st.markdown(
        f"""
        <div class="info-box">
            ℹ️ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_warning_message(message: str):
    """Render a warning message box."""
    st.markdown(
        f"""
        <div class="warning-box">
            ⚠️ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
