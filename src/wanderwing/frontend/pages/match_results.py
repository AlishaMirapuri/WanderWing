"""Match Results page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_info_message, render_warning_message
from wanderwing.frontend.utils.session import (
    get_matches,
    select_match,
    save_activities,
    get_parsed_intent,
    has_matches,
)
from wanderwing.frontend.utils.mock_data import generate_mock_activities
from wanderwing.frontend.components.cards import render_match_card


def render():
    """Render the Match Results page."""
    render_page_header(
        "Your Match Results",
        "Compatible travelers going to the same destination"
    )

    if not has_matches():
        render_warning_message(
            "No matches found yet. Please complete the previous steps to find compatible travelers."
        )
        return

    matches = get_matches()
    parsed_intent = get_parsed_intent()

    st.markdown(f"### Found {len(matches)} Compatible Travelers")

    render_info_message(
        f"These travelers are all heading to **{parsed_intent['primary_destination']}** "
        f"with overlapping dates and similar interests."
    )

    st.markdown("---")

    for i, match in enumerate(matches):
        render_match_card(match)

        col1, col2 = st.columns([3, 1])

        with col2:
            if st.button(
                f"See Activities with {match['name']}",
                key=f"activities_{i}",
                use_container_width=True,
            ):
                with st.spinner("Generating activity recommendations..."):
                    import time
                    time.sleep(1.5)

                    activities = generate_mock_activities(match, parsed_intent, num_activities=5)
                    save_activities(activities)
                    select_match(match)

                    st.success(
                        f"Generated {len(activities)} activity recommendations! "
                        f"Go to **Activity Recommendations** to see them."
                    )
                    st.balloons()

    st.markdown("---")
    st.info(
        """
        💡 **Tip:** Click "See Activities" to get personalized activity recommendations
        for you and your matched traveler!
        """
    )
