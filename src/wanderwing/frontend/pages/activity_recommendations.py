"""Activity Recommendations page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_warning_message
from wanderwing.frontend.utils.session import (
    get_activities,
    get_selected_match,
    get_parsed_intent,
    has_activities,
)
from wanderwing.frontend.components.cards import render_activity_card


def render():
    """Render the Activity Recommendations page."""
    render_page_header(
        "Shared Activity Recommendations",
        "Discover things to do together with your matched traveler"
    )

    if not has_activities():
        render_warning_message(
            "No activity recommendations yet. Please select a match from **Match Results** first."
        )
        return

    activities = get_activities()
    selected_match = get_selected_match()
    parsed_intent = get_parsed_intent()

    if selected_match:
        st.markdown(f"### Activities for You & {selected_match['name']}")
        st.markdown(
            f"""
            <div style="background: #EEF2FF; padding: 1rem; border-radius: 8px;
                        border-left: 3px solid #3B82F6; margin-bottom: 1.5rem;">
                📍 <strong>{parsed_intent['primary_destination']}</strong><br>
                👥 Compatibility Score: <strong>{int(selected_match['overall_score'] * 100)}%</strong><br>
                🎯 Shared Interests: <strong>{', '.join(selected_match['shared_activities'][:3])}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("### Recommended Activities")

    st.markdown("---")

    for activity in activities:
        render_activity_card(activity)

    st.markdown("---")

    st.info(
        """
        💡 **Next Steps:**
        1. Copy a meeting suggestion and send it to your match
        2. Book activities that require reservations in advance
        3. Rate your experience after the trip in the **Feedback** section!
        """
    )

    if st.button("⭐ Leave Feedback", use_container_width=True, type="primary"):
        st.info("Go to the **Feedback** page to rate your match and share your experience!")
