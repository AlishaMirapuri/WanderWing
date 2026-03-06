"""Parsed Intent Review page — renders differently per UX variant."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message, render_warning_message
from wanderwing.frontend.utils.session import (
    get_trip_text,
    get_parsed_intent,
    save_matches,
    get_profile,
    is_trip_described,
    log_experiment_event,
)
from wanderwing.frontend.utils.mock_data import generate_mock_matches
from wanderwing.frontend.components.cards import render_intent_comparison


def _render_itinerary_summary(parsed_intent: dict) -> None:
    """Render a styled itinerary summary card (Variants A and C)."""
    destination = parsed_intent.get("primary_destination", "N/A")
    start_date = parsed_intent.get("overall_start_date", "N/A")
    end_date = parsed_intent.get("overall_end_date", "N/A")
    duration = parsed_intent.get("duration_days", "N/A")
    activities = parsed_intent.get("activities", [])
    budget = parsed_intent.get("budget_tier", "N/A").replace("_", " ").title()
    pace = parsed_intent.get("pace_preference", "N/A").replace("_", " ").title()

    acts_pills = "".join(
        '<span style="display:inline-block;background:rgba(255,107,107,0.12);color:#FF6B6B;'
        'padding:0.15rem 0.6rem;border-radius:100px;font-size:0.78rem;font-weight:500;'
        f'margin:0.12rem 0.15rem 0.12rem 0;">{a.replace("_", " ").title()}</span>'
        for a in activities[:4]
    ) or "\u2014"

    rows = [
        ("Destination", f"<strong style='color:#1A1A2E;'>{destination}</strong>"),
        ("Dates",       f"{start_date} \u2192 {end_date}"),
        ("Duration",    f"{duration} days"),
        ("Activities",  acts_pills),
        ("Budget",      budget),
        ("Pace",        pace),
    ]
    rows_html = "".join(
        '<tr>'
        f'<td style="padding:0.4rem 0.75rem 0.4rem 0;font-size:0.68rem;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.09em;color:rgba(26,26,46,0.32);'
        f'white-space:nowrap;vertical-align:top;">{lbl}</td>'
        f'<td style="padding:0.4rem 0;font-size:0.88rem;color:rgba(26,26,46,0.65);">{val}</td>'
        '</tr>'
        for lbl, val in rows
    )

    st.markdown(
        '<div class="ww-card ww-anim" style="margin-bottom:1.25rem;">'
        '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.9rem;">Itinerary summary</div>'
        f'<table style="width:100%;border-collapse:collapse;">{rows_html}</table>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_match_archetypes(parsed_intent: dict) -> None:
    """Render a preview of likely match archetypes (Variant C only)."""
    destination = parsed_intent.get("primary_destination", "your destination")
    activities = parsed_intent.get("activities", [])

    if "HIKING" in activities or "ADVENTURE_SPORTS" in activities:
        archetype1 = "adventure-minded solo travelers"
        archetype2 = "outdoor enthusiasts planning day hikes"
    elif "FOOD_TOURS" in activities or "LOCAL_EXPERIENCES" in activities:
        archetype1 = "food-focused cultural explorers"
        archetype2 = "local-experience seekers"
    else:
        archetype1 = "curious, open-minded solo travelers"
        archetype2 = "sightseeing enthusiasts"

    st.markdown(
        '<div class="ww-card ww-anim" style="margin-bottom:1.25rem;border-left:3px solid #FF6B6B;">'
        '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">'
        f'Who you\'ll likely match with in {destination}</div>'
        f'<div style="font-size:0.9rem;font-weight:700;color:#1A1A2E;margin-bottom:0.2rem;">{archetype1.capitalize()}</div>'
        f'<div style="font-size:0.88rem;color:rgba(26,26,46,0.55);">Also common \u2014 {archetype2.capitalize()}</div>'
        '<p style="margin:0.65rem 0 0;font-size:0.78rem;color:rgba(26,26,46,0.40);">'
        'Based on your activity preferences. Confirm below to see real matches.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def _find_matches_button(parsed_intent: dict) -> bool:
    """Render the Find Matches button and return True if clicked."""
    clicked = st.button("Looks good \u2014 find matches", type="primary", use_container_width=True)
    if clicked:
        with st.spinner("Finding compatible travelers\u2026"):
            import time
            time.sleep(2)
            matches = generate_mock_matches(get_profile(), parsed_intent, num_matches=5)
            save_matches(matches)
            log_experiment_event("parse_accepted", {
                "destination": parsed_intent.get("primary_destination"),
                "duration": parsed_intent.get("duration_days"),
            })
            render_success_message(
                f"Found {len(matches)} compatible travelers."
            )
            st.balloons()
            st.session_state["matches_ready"] = True
    return clicked


def _render_go_to_matches() -> None:
    """Render the Continue to Matches CTA after matches are found."""
    if st.session_state.get("matches_ready"):
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("→ Continue to Matches", type="primary", use_container_width=True):
            st.session_state.pop("matches_ready", None)
            st.session_state["_nav_target"] = "Matches"
            st.rerun()


def render():
    """Render the Parsed Intent Review page with variant-specific UX."""
    render_page_header(
        "Does this look right?",
        "Confirm the details we extracted from your description.",
        step="3 / 5",
    )

    if not is_trip_described():
        render_warning_message("Describe your trip first.")
        return

    raw_text = get_trip_text()
    parsed_intent = get_parsed_intent()

    if not parsed_intent:
        render_warning_message("No parsed intent found. Go back to Trip and parse your description.")
        return

    variant = st.session_state.get("experiment_variant", "variant_a")

    # ── Variant A: Full summary card + comparison view ────────────────────────
    if variant == "variant_a":
        _render_itinerary_summary(parsed_intent)

        st.markdown(
            '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:1.5rem 0 0.75rem;">Side-by-side view</div>',
            unsafe_allow_html=True,
        )
        render_intent_comparison(raw_text, parsed_intent)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Edit description", use_container_width=True):
                st.session_state["_nav_target"] = "Trip"
                st.rerun()
        with col2:
            _find_matches_button(parsed_intent)
        _render_go_to_matches()

    # ── Variant B: One-liner summary + immediate CTA ──────────────────────────
    elif variant == "variant_b":
        destination = parsed_intent.get("primary_destination", "your destination")
        start_date = parsed_intent.get("overall_start_date", "?")
        end_date = parsed_intent.get("overall_end_date", "?")
        activities = parsed_intent.get("activities", [])
        activity_str = ", ".join(a.replace("_", " ").title() for a in activities[:2])

        st.markdown(
            '<div class="ww-card ww-anim" style="margin-bottom:1.25rem;">'
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.5rem;">We understood</div>'
            f'<div style="font-size:1.1rem;font-weight:700;color:#1A1A2E;line-height:1.4;">'
            f'{destination}'
            f'<span style="color:rgba(26,26,46,0.20);margin:0 0.4rem;">\u00b7</span>'
            f'{start_date} \u2013 {end_date}'
            f'<span style="color:rgba(26,26,46,0.20);margin:0 0.4rem;">\u00b7</span>'
            f'{activity_str or "Sightseeing"}'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        _find_matches_button(parsed_intent)
        _render_go_to_matches()

    # ── Variant C: Summary card + match archetype preview + comparison ─────────
    else:  # variant_c
        _render_itinerary_summary(parsed_intent)
        _render_match_archetypes(parsed_intent)

        st.markdown(
            '<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin:1.5rem 0 0.75rem;">Side-by-side view</div>',
            unsafe_allow_html=True,
        )
        render_intent_comparison(raw_text, parsed_intent)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Edit description", use_container_width=True):
                st.session_state["_nav_target"] = "Trip"
                st.rerun()
        with col2:
            _find_matches_button(parsed_intent)
        _render_go_to_matches()
