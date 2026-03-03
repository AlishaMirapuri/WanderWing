"""
WanderWing Streamlit Frontend - Main Application

A modern, polished interface for traveler matching and activity recommendations.

Run with:
    streamlit run src/wanderwing/frontend/app.py
"""

import streamlit as st
from wanderwing.frontend.utils.session import initialize_session_state
from wanderwing.frontend.utils.styling import apply_custom_css

# Page configuration
st.set_page_config(
    page_title="WanderWing - Travel Companion Matching",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
initialize_session_state()

# Apply custom styling
apply_custom_css()

# Sidebar navigation
st.sidebar.title("🌍 WanderWing")
st.sidebar.markdown("**Travel Companion Matching**")
st.sidebar.markdown("---")

# Navigation menu
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "👤 Create Profile",
        "✈️ Describe Trip",
        "🔍 Review Intent",
        "🤝 Match Results",
        "🎯 Activity Recommendations",
        "⭐ Feedback",
        "📊 Dashboard",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Demo Mode**

    This is a demonstration interface with mock data.
    Navigate through each step to see the full workflow.
    """
)

# Main content area
if page == "🏠 Home":
    st.markdown("# 🌍 Welcome to WanderWing")
    st.markdown(
        """
        <p style='font-size: 1.2rem; color: #6B7280; margin-bottom: 2rem;'>
        Find compatible travel companions and discover shared adventures
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
                <div style="font-size: 3rem; text-align: center;">👤</div>
                <h3 style="text-align: center; color: #1E3A8A;">Create Profile</h3>
                <p style="text-align: center; color: #6B7280;">
                    Share your travel preferences and verification level
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <div style="font-size: 3rem; text-align: center;">✈️</div>
                <h3 style="text-align: center; color: #1E3A8A;">Describe Trip</h3>
                <p style="text-align: center; color: #6B7280;">
                    Tell us about your upcoming adventure in natural language
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <div style="font-size: 3rem; text-align: center;">🤝</div>
                <h3 style="text-align: center; color: #1E3A8A;">Get Matches</h3>
                <p style="text-align: center; color: #6B7280;">
                    Find compatible travelers going to the same destination
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card">
                <div style="font-size: 3rem; text-align: center;">🎯</div>
                <h3 style="text-align: center; color: #1E3A8A;">Discover Activities</h3>
                <p style="text-align: center; color: #6B7280;">
                    Get personalized activity recommendations for your matched travelers
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <div style="font-size: 3rem; text-align: center;">⭐</div>
                <h3 style="text-align: center; color: #1E3A8A;">Share Feedback</h3>
                <p style="text-align: center; color: #6B7280;">
                    Rate your matches and help us improve recommendations
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown("### 🚀 Getting Started")
    st.markdown(
        """
        1. **Create your profile** with basic information and verification level
        2. **Describe your trip** in natural language (where, when, what you want to do)
        3. **Review the parsed intent** to ensure we understood correctly
        4. **Browse your matches** and see compatibility scores
        5. **Get activity recommendations** to do with your matched travelers
        6. **Rate and provide feedback** to help improve the system

        Use the navigation menu on the left to get started! 👈
        """
    )

    st.markdown("---")

    st.info(
        """
        **Demo Note:** This interface uses mock data for demonstration purposes.
        In production, it would connect to the actual WanderWing matching engine and activity recommendation system.
        """
    )

elif page == "👤 Create Profile":
    from wanderwing.frontend.pages import create_profile
    create_profile.render()

elif page == "✈️ Describe Trip":
    from wanderwing.frontend.pages import describe_trip
    describe_trip.render()

elif page == "🔍 Review Intent":
    from wanderwing.frontend.pages import parsed_intent_review
    parsed_intent_review.render()

elif page == "🤝 Match Results":
    from wanderwing.frontend.pages import match_results
    match_results.render()

elif page == "🎯 Activity Recommendations":
    from wanderwing.frontend.pages import activity_recommendations
    activity_recommendations.render()

elif page == "⭐ Feedback":
    from wanderwing.frontend.pages import feedback
    feedback.render()

elif page == "📊 Dashboard":
    from wanderwing.frontend.pages import experiment_dashboard
    experiment_dashboard.render()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #9CA3AF; font-size: 0.85rem;'>
        WanderWing v1.0<br>
        Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
