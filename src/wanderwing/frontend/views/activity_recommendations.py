"""Activity Recommendations page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_warning_message, render_empty_state
from wanderwing.frontend.utils.session import (
    get_activities,
    get_selected_match,
    get_parsed_intent,
    has_activities,
    log_experiment_event,
)
from wanderwing.frontend.components.cards import render_activity_card


def render():
    """Render the Activity Recommendations page."""
    variant = st.session_state.get("experiment_variant", "variant_a")

    if variant == "variant_c":
        render_page_header(
            "Plan together.",
            "Deep-dive into shared activities and coordinate your first meeting.",
            step="5 / 5",
        )
    else:
        render_page_header(
            "Shared activities.",
            "Discover things to do together with your matched traveler.",
            step="5 / 5",
        )

    if not has_activities():
        render_empty_state(
            "No activities yet.",
            "Go to Matches, pick a compatible traveler, and generate activity ideas together.",
        )
        return

    activities = get_activities()
    selected_match = get_selected_match()
    parsed_intent = get_parsed_intent()

    if selected_match:
        shared_str = ", ".join(
            a.replace("_", " ").title()
            for a in selected_match["shared_activities"][:3]
        )
        st.markdown(
            '<div class="ww-card ww-anim" style="margin-bottom:2rem;">'
            '<div style="display:flex;gap:2.5rem;flex-wrap:wrap;">'
            '<div>'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);">Destination</div>'
            f'<div style="font-weight:700;color:#1A1A2E;margin-top:0.25rem;">{parsed_intent["primary_destination"]}</div>'
            '</div>'
            '<div>'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);">Compatibility</div>'
            f'<div style="font-weight:700;color:#FF6B6B;margin-top:0.25rem;">{int(selected_match["overall_score"] * 100)}%</div>'
            '</div>'
            '<div>'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);">Shared interests</div>'
            f'<div style="font-weight:700;color:#1A1A2E;margin-top:0.25rem;">{shared_str}</div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if variant == "variant_c":
            st.markdown(
                '<div style="background:rgba(255,107,107,0.07);border-radius:16px;'
                'padding:1rem 1.25rem;margin-bottom:1.5rem;'
                'border:1px solid rgba(255,107,107,0.15);">'
                '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.10em;color:#FF6B6B;margin-bottom:0.4rem;">Coordination tip</div>'
                '<p style="margin:0;color:rgba(26,26,46,0.65);font-size:0.9rem;line-height:1.6;">'
                'Pick an activity below and use the suggested message to reach out to '
                f'<strong style="color:#1A1A2E;">{selected_match["name"]}</strong>. '
                'Always meet in a public place first.'
                '</p>'
                '</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="font-size:1.1rem;font-weight:700;color:#1A1A2E;'
            'margin-bottom:1.5rem;">Recommended activities</div>',
            unsafe_allow_html=True,
        )

    for activity in activities:
        render_activity_card(activity)

        activity_id = activity.get("activity_id", "unknown")
        activity_name = activity.get("name", "activity")
        like_key = f"like_{activity_id}"

        col1, col2 = st.columns([5, 1])
        with col2:
            if not st.session_state.get(f"liked_{like_key}"):
                if st.button("Save", key=like_key, help=f"Save '{activity_name}'"):
                    st.session_state[f"liked_{like_key}"] = True
                    log_experiment_event(
                        "recommendation_liked",
                        {
                            "activity_id": activity_id,
                            "name": activity_name,
                            "rating": 1,
                        },
                    )
                    st.rerun()
            else:
                st.markdown(
                    '<span style="color:#FF6B6B;font-size:0.82rem;font-weight:600;">Saved</span>',
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    if variant == "variant_c":
        st.markdown(
            '<div class="ww-card ww-anim">'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">Plan together</div>'
            '<ol style="margin:0;padding-left:1.25rem;color:rgba(26,26,46,0.65);font-size:0.9rem;line-height:1.9;">'
            '<li>Send the suggested message to your match</li>'
            '<li>Confirm a time and public meeting spot</li>'
            '<li>Share contact details only after meeting in person</li>'
            f'<li>Rate your experience in <strong style="color:#1A1A2E;">Feedback</strong> after the trip</li>'
            '</ol>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="ww-card ww-anim">'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">Next steps</div>'
            '<ol style="margin:0;padding-left:1.25rem;color:rgba(26,26,46,0.65);font-size:0.9rem;line-height:1.9;">'
            '<li>Copy a meeting suggestion and send it to your match</li>'
            '<li>Book activities that need advance reservations</li>'
            f'<li>Rate your experience in <strong style="color:#1A1A2E;">Feedback</strong> after the trip</li>'
            '</ol>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if st.button("Leave feedback", use_container_width=True, type="primary"):
        st.session_state["_nav_target"] = "Feedback"
        st.rerun()
