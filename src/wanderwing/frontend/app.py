"""Streamlit frontend main application."""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="WanderWing",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main page
st.markdown('<div class="main-header">✈️ WanderWing</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Connect with travelers heading to the same destination</div>',
    unsafe_allow_html=True,
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = 1  # Default user for MVP

if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"

# Welcome section
col1, col2 = st.columns(2)

with col1:
    st.subheader("How It Works")
    st.markdown(
        """
        1. **Describe Your Trip** - Tell us where you're going in natural language
        2. **Get Matched** - Our AI finds compatible travelers with similar plans
        3. **Connect** - Reach out to potential travel companions
        4. **Share Experiences** - Plan activities together and save costs
        """
    )

with col2:
    st.subheader("Why WanderWing?")
    st.markdown(
        """
        - **AI-Powered Matching** - Smart compatibility based on preferences
        - **Safety First** - Profile verification and reporting
        - **Save Money** - Share costs for tours, transportation, accommodations
        - **Make Friends** - Travel is better with companions
        """
    )

# Quick actions
st.divider()
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Create New Trip", use_container_width=True):
        st.switch_page("pages/1_create_trip.py")

with col2:
    if st.button("🔍 Discover Matches", use_container_width=True):
        st.switch_page("pages/2_discover_matches.py")

with col3:
    if st.button("📊 View Metrics", use_container_width=True):
        st.switch_page("pages/3_metrics.py")

# Footer
st.divider()
st.caption("WanderWing v0.1.0 - AI-Powered Travel Companion Matching")
