"""Match Results page — with event logging and Variant C enhancements."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_info_message, render_warning_message, render_section_header, render_empty_state, render_skeleton_card
from wanderwing.frontend.utils.session import (
    get_matches,
    select_match,
    save_activities,
    get_parsed_intent,
    has_matches,
    log_experiment_event,
)
from wanderwing.frontend.utils.mock_data import generate_mock_activities
from wanderwing.frontend.components.cards import render_match_card


def _render_why_this_match(match: dict, parsed_intent: dict) -> None:
    """Variant C: expandable 'Why this match?' section."""
    component_scores = match.get("component_scores", {})
    dims = [
        ("Destination", component_scores.get("destination", 0)),
        ("Date overlap", component_scores.get("date_overlap", 0)),
        ("Activities",   component_scores.get("activity_similarity", 0)),
        ("Budget",       component_scores.get("budget_compatibility", 0)),
        ("Pace",         component_scores.get("pace_compatibility", 0)),
    ]

    bars_html = ""
    for label, score in dims:
        pct = int(score * 100)
        bar_color = "#FF6B6B" if pct >= 75 else "rgba(26,26,46,0.20)"
        bars_html += (
            f'<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">'
            f'<span style="width:80px;font-size:0.75rem;color:rgba(26,26,46,0.40);'
            f'font-weight:500;flex-shrink:0;">{label}</span>'
            f'<div style="flex:1;background:rgba(26,26,46,0.07);border-radius:100px;height:4px;">'
            f'<div style="background:{bar_color};width:{pct}%;height:4px;border-radius:100px;"></div>'
            f'</div>'
            f'<span style="width:28px;font-size:0.75rem;color:rgba(26,26,46,0.55);'
            f'font-weight:600;text-align:right;flex-shrink:0;">{pct}%</span>'
            f'</div>'
        )

    preview_activities = generate_mock_activities(match, parsed_intent, num_activities=2)
    activity_bullets = "".join(
        f'<div style="margin-bottom:0.4rem;">'
        f'<span style="font-weight:700;color:#1A1A2E;font-size:0.88rem;">{a["name"]}</span>'
        f'<span style="color:rgba(26,26,46,0.45);font-size:0.88rem;"> \u2014 {a["description"][:70]}\u2026</span>'
        f'</div>'
        for a in preview_activities
    )

    with st.expander(f"Why {match['name']} is a strong match"):
        st.markdown(
            '<div style="padding:0.25rem 0;">'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">Compatibility breakdown</div>'
            f'{bars_html}'
            '<div style="height:1px;background:rgba(26,26,46,0.08);margin:1rem 0;"></div>'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.6rem;">Top activity ideas</div>'
            f'{activity_bullets}'
            '</div>',
            unsafe_allow_html=True,
        )


def render():
    """Render the Match Results page."""
    render_page_header(
        "Your matches.",
        "Compatible travelers heading to the same destination.",
        step="4 / 5",
    )

    if not has_matches():
        render_empty_state(
            "No matches yet.",
            "Complete your profile and describe your trip to find compatible travelers.",
        )
        return

    matches = get_matches()
    parsed_intent = get_parsed_intent()
    variant = st.session_state.get("experiment_variant", "variant_a")

    render_section_header(
        "Compatible travelers",
        f'{len(matches)} heading to {parsed_intent["primary_destination"]} with overlapping dates.',
        num=str(len(matches)),
    )

    for i, match in enumerate(matches):
        render_match_card(match)

        if variant == "variant_c":
            _render_why_this_match(match, parsed_intent)

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button(
                f"Activities with {match['name'].split()[0]}",
                key=f"activities_{i}",
                use_container_width=True,
            ):
                # Show skeleton cards while generating, then replace with result
                loading_slot = st.empty()
                with loading_slot.container():
                    render_skeleton_card(lines=4)
                    render_skeleton_card(lines=3)

                import time
                time.sleep(1.5)

                activities = generate_mock_activities(match, parsed_intent, num_activities=5)
                loading_slot.empty()
                save_activities(activities)
                select_match(match)

                log_experiment_event(
                    "match_clicked",
                    {
                        "rank": i + 1,
                        "score": match.get("overall_score"),
                        "name": match.get("name"),
                        "match_id": match.get("match_id"),
                    },
                )

                st.success(f"Generated {len(activities)} activity recommendations.")
                st.balloons()
                st.session_state["activities_ready"] = True

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.78rem;color:rgba(26,26,46,0.35);margin-top:1.5rem;">'
        'Select a match to get personalized activity recommendations for your trip together.</p>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("activities_ready"):
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("→ Continue to Activities", type="primary", use_container_width=True):
            st.session_state.pop("activities_ready", None)
            st.session_state["_nav_target"] = "Activities"
            st.rerun()
