"""Describe Trip page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message, render_warning_message
from wanderwing.frontend.utils.session import (
    save_trip_description,
    save_parsed_intent,
    get_trip_text,
    is_profile_complete,
)
from wanderwing.frontend.utils.mock_data import generate_parsed_intent


def render():
    """Render the Describe Trip page."""
    render_page_header(
        "Describe Your Trip",
        "Tell us about your upcoming adventure in your own words"
    )

    if not is_profile_complete():
        render_warning_message("Please complete your profile first!")
        return

    st.markdown(
        """
        Describe your trip plans naturally. Include:
        - **Where** you're going
        - **When** you're traveling
        - **What activities** you're interested in
        - **Your budget** level
        - **Your pace** preference

        Our AI will extract the key details automatically!
        """
    )

    st.markdown("### Example Descriptions")

    with st.expander("📝 See Examples"):
        st.markdown(
            """
            **Example 1:**
            > I'm planning to visit Tokyo from April 1-10. I love hiking and want to do a Mt. Fuji day trip.
            > Also interested in food tours and trying authentic ramen. My budget is moderate, around $100/day.
            > I prefer a relaxed pace with some free time to explore.

            **Example 2:**
            > Heading to Paris for a week in May. Budget traveler here - hostels and cheap eats!
            > Want to see all the museums (Louvre, Musée d'Orsay) and do walking tours.
            > Fast-paced, trying to see as much as possible!

            **Example 3:**
            > Barcelona trip, June 15-25. Beach lover + foodie combo. Looking for tapas tours,
            > beach days, and maybe some hiking at Montserrat. Moderate budget, relaxed pace.
            """
        )

    st.markdown("---")

    trip_text = st.text_area(
        "Your Trip Description",
        value=get_trip_text(),
        height=200,
        placeholder="I'm planning to visit...",
    )

    if st.button("Parse My Trip", type="primary", use_container_width=True):
        if not trip_text or len(trip_text) < 20:
            st.error("Please provide a more detailed trip description (at least 20 characters)")
        else:
            with st.spinner("Analyzing your trip description..."):
                # Simulate processing time
                import time
                time.sleep(1.5)

                # Generate mock parsed intent
                parsed_intent = generate_parsed_intent(trip_text)

                save_trip_description(trip_text)
                save_parsed_intent(parsed_intent)

                render_success_message(
                    "Trip parsed successfully! Go to **Review Intent** to verify the extracted information."
                )
                st.balloons()

    if get_trip_text():
        st.markdown("---")
        st.markdown("### Your Description")
        st.markdown(
            f"""
            <div style="background: #F9FAFB; padding: 1rem; border-radius: 8px;
                        border-left: 3px solid #3B82F6;">
                {get_trip_text()}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("✅ Trip described! Continue to **Review Intent** to see the parsed details.")
