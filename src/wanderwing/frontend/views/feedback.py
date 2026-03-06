"""Feedback page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message
from wanderwing.frontend.utils.session import save_feedback, get_selected_match, log_experiment_event


def render():
    """Render the Feedback page."""
    render_page_header(
        "How did it go?",
        "Your feedback shapes future matches.",
    )

    selected_match = get_selected_match()

    if selected_match:
        st.markdown(
            f'<div style="font-size:0.9rem;color:rgba(26,26,46,0.55);'
            f'margin-bottom:1.5rem;">Rating your match with '
            f'<strong style="color:#1A1A2E;">{selected_match["name"]}</strong></div>',
            unsafe_allow_html=True,
        )

    with st.form("feedback_form"):
        rating = st.slider(
            "Match quality",
            min_value=1,
            max_value=5,
            value=4,
            help="1 = Poor · 5 = Excellent",
        )

        rating_labels = {1: "Poor", 2: "Fair", 3: "Good", 4: "Great", 5: "Excellent"}
        st.markdown(
            f'<div style="font-size:0.78rem;color:rgba(26,26,46,0.45);'
            f'font-weight:500;margin-bottom:1rem;">'
            f'{rating}/5 — {rating_labels[rating]}</div>',
            unsafe_allow_html=True,
        )

        accepted = st.radio(
            "Did you connect with this traveler?",
            options=["Yes, we connected!", "No, I declined", "Still deciding"],
        )

        comments = st.text_area(
            "Comments (optional)",
            placeholder="What worked well? What could be improved?",
            height=120,
        )

        submitted = st.form_submit_button("Submit feedback", type="primary", use_container_width=True)

        if submitted:
            match_id = selected_match["match_id"] if selected_match else "general"
            accepted_bool = accepted == "Yes, we connected!"

            save_feedback(match_id, rating, comments, accepted_bool)

            log_experiment_event(
                "feedback_submitted",
                {
                    "rating": rating,
                    "accepted": accepted_bool,
                    "match_id": match_id,
                },
            )

            render_success_message("Thank you — this helps us improve the matching algorithm.")
            st.balloons()

            if accepted_bool:
                st.markdown(
                    '<div class="ww-card ww-anim" style="margin-top:1rem;">'
                    '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
                    'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">Tips for your first meeting</div>'
                    '<ul style="margin:0;padding-left:1.25rem;color:rgba(26,26,46,0.65);font-size:0.9rem;line-height:1.9;">'
                    '<li>Meet in a public place first</li>'
                    '<li>Share your plans with a friend or family member</li>'
                    '<li>Keep communication open and respectful</li>'
                    '<li>Have a great adventure!</li>'
                    '</ul></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p style="font-size:0.88rem;color:rgba(26,26,46,0.55);margin-top:1rem;">'
                    "Your feedback helps future matching. You can always go back to "
                    "<strong style='color:#1A1A2E;'>Matches</strong> to explore other travelers.</p>",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:1rem;">Platform statistics</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg. rating", "4.3 / 5", "+0.2")
    with col2:
        st.metric("Acceptance rate", "68%", "+5%")
    with col3:
        st.metric("Total feedback", "437", "+23")
