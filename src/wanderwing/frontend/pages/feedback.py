"""Feedback page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message
from wanderwing.frontend.utils.session import save_feedback, get_selected_match


def render():
    """Render the Feedback page."""
    render_page_header(
        "Share Your Feedback",
        "Help us improve by rating your match and experience"
    )

    selected_match = get_selected_match()

    if selected_match:
        st.markdown(f"### Rating Your Match with {selected_match['name']}")
    else:
        st.markdown("### General Feedback")

    with st.form("feedback_form"):
        st.markdown("#### Match Quality")

        rating = st.slider(
            "How would you rate this match?",
            min_value=1,
            max_value=5,
            value=4,
            help="1 = Poor match, 5 = Excellent match",
        )

        stars = "⭐" * rating
        st.markdown(f"**Your Rating:** {stars}")

        st.markdown("---")

        st.markdown("#### Decision")

        accepted = st.radio(
            "Did you accept this match and connect with them?",
            options=["Yes, we connected!", "No, I declined", "Still deciding"],
        )

        st.markdown("---")

        st.markdown("#### Comments")

        comments = st.text_area(
            "Tell us more about your experience (optional)",
            placeholder="What worked well? What could be improved?",
            height=150,
        )

        submitted = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)

        if submitted:
            match_id = selected_match['match_id'] if selected_match else "general"
            accepted_bool = accepted == "Yes, we connected!"

            save_feedback(match_id, rating, comments, accepted_bool)

            render_success_message("Thank you for your feedback! This helps us improve our matching algorithm.")
            st.balloons()

            # Show what happens next
            st.markdown("---")
            st.markdown("### What's Next?")

            if accepted_bool:
                st.success(
                    """
                    🎉 Great! Here are some tips for meeting your travel companion:
                    - Meet in a public place first
                    - Share your plans with a friend or family member
                    - Keep communication open and respectful
                    - Have fun and enjoy your adventure!
                    """
                )
            else:
                st.info(
                    """
                    No worries! We'll use your feedback to improve future matches.
                    You can always go back to **Match Results** to explore other compatible travelers.
                    """
                )

    st.markdown("---")

    st.markdown("### Feedback Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Average Rating", "4.3 ⭐", "+0.2")

    with col2:
        st.metric("Acceptance Rate", "68%", "+5%")

    with col3:
        st.metric("Total Feedback", "437", "+23")
