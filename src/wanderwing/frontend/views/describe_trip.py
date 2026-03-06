"""Describe Trip page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message, render_warning_message, render_feature_highlight
from wanderwing.frontend.utils.session import (
    save_trip_description,
    save_parsed_intent,
    get_trip_text,
    is_profile_complete,
    log_experiment_event,
)
from wanderwing.frontend.utils.mock_data import generate_parsed_intent


def render():
    """Render the Describe Trip page."""
    render_page_header(
        "Where are you going?",
        "Describe your trip in plain language — we'll extract the details.",
        step="2 / 5",
    )

    if not is_profile_complete():
        render_warning_message("Complete your profile first.")
        return

    with st.expander("See example descriptions"):
        st.markdown(
            """
**Tokyo, 10 days**
> I'm visiting Tokyo from April 1–10. Love hiking — want to do a Mt. Fuji day trip.
> Also interested in food tours and ramen. Moderate budget. Relaxed pace.

**Paris, one week**
> Heading to Paris for a week in May. Budget traveler — hostels, cheap eats.
> Museums (Louvre, Musée d'Orsay), walking tours. Fast-paced, maximising every day.

**Barcelona, June**
> Barcelona, June 15–25. Beach lover and foodie. Tapas tours, beach days,
> maybe hiking at Montserrat. Moderate budget, relaxed pace.
"""
        )

    render_feature_highlight(
        '<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.12em;color:#FF6B6B;margin-bottom:0.5rem;">Powered by AI</div>'
        '<p style="font-size:1rem;font-weight:700;color:#1A1A2E;margin:0 0 0.4rem;">Plain English → Structured intent</p>'
        '<p style="font-size:0.875rem;line-height:1.65;color:rgba(26,26,46,0.55);margin:0;">'
        'No forms to fill. Write naturally — we extract destination, dates, activities, budget, and travel pace automatically.'
        '</p>'
    )

    trip_text = st.text_area(
        "Your trip description",
        value=get_trip_text(),
        height=200,
        placeholder="I'm planning to visit…",
        label_visibility="collapsed",
    )

    parse_count = st.session_state.get("parse_count", 0)

    if st.button("Submit my trip", type="primary", use_container_width=True):
        if not trip_text or len(trip_text) < 20:
            st.error("Please write at least a sentence about your trip.")
        else:
            with st.spinner("Reading your description…"):
                import time
                time.sleep(1.5)

                parsed_intent = generate_parsed_intent(trip_text)

                if parse_count > 0:
                    log_experiment_event(
                        "parse_edited",
                        {
                            "destination": parsed_intent.get("primary_destination"),
                            "parse_attempt": parse_count + 1,
                        },
                    )

                save_trip_description(trip_text)
                save_parsed_intent(parsed_intent)
                st.session_state.parse_count = parse_count + 1

                render_success_message("Parsed. Continue to Review to confirm the details.")
                st.balloons()

    if get_trip_text():
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="ww-card ww-anim">'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">Your description</div>'
            f'<p style="color:rgba(26,26,46,0.65);line-height:1.75;white-space:pre-wrap;'
            f'font-size:0.9rem;margin:0;">{get_trip_text()}</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        col_nav, _ = st.columns([1, 2])
        with col_nav:
            if st.button("Continue to Review →", type="primary", use_container_width=True):
                st.session_state["_nav_target"] = "Review"
                st.rerun()
