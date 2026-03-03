"""Parsed Intent Review page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message, render_warning_message
from wanderwing.frontend.utils.session import (
    get_trip_text,
    get_parsed_intent,
    save_matches,
    get_profile,
    is_trip_described,
)
from wanderwing.frontend.utils.mock_data import generate_mock_matches
from wanderwing.frontend.components.cards import render_intent_comparison


def render():
    """Render the Parsed Intent Review page."""
    render_page_header(
        "Review Parsed Intent",
        "Verify that we understood your trip correctly"
    )

    if not is_trip_described():
        render_warning_message("Please describe your trip first!")
        return

    raw_text = get_trip_text()
    parsed_intent = get_parsed_intent()

    if not parsed_intent:
        render_warning_message("No parsed intent found. Please go back to **Describe Trip** and parse your description.")
        return

    st.markdown("### Comparison View")
    st.markdown("We extracted structured information from your description. Please verify it's correct.")

    render_intent_comparison(raw_text, parsed_intent)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("❌ Not Correct - Edit Description", use_container_width=True):
            st.info("Please go back to **Describe Trip** to edit your description.")

    with col2:
        if st.button("✅ Looks Good - Find Matches", type="primary", use_container_width=True):
            with st.spinner("Finding compatible travelers..."):
                import time
                time.sleep(2)

                # Generate mock matches
                matches = generate_mock_matches(get_profile(), parsed_intent, num_matches=5)
                save_matches(matches)

                render_success_message(
                    f"Found {len(matches)} compatible travelers! Go to **Match Results** to see them."
                )
                st.balloons()
