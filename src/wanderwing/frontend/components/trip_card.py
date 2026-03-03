"""Trip card component for displaying trip information."""

import streamlit as st


def render_trip_card(trip: dict) -> None:
    """
    Render a trip card with trip information.

    Args:
        trip: Trip data dictionary
    """
    with st.container():
        parsed = trip.get("parsed_data")

        if parsed:
            st.subheader(f"🌍 {parsed.get('destination', 'Unknown')}")

            col1, col2, col3 = st.columns(3)

            with col1:
                if parsed.get("start_date") and parsed.get("end_date"):
                    st.write(f"**Dates:** {parsed['start_date']} to {parsed['end_date']}")
                elif parsed.get("duration_days"):
                    st.write(f"**Duration:** {parsed['duration_days']} days")

            with col2:
                st.write(f"**Budget:** {parsed.get('budget_tier', 'Unknown').title()}")

            with col3:
                if parsed.get("activities"):
                    st.write(f"**Activities:** {len(parsed['activities'])}")

            # Show activities
            if parsed.get("activities"):
                activities_str = ", ".join(
                    [act.replace("_", " ").title() for act in parsed["activities"][:5]]
                )
                st.write(f"*{activities_str}*")

        else:
            st.write("**Raw Input:**")
            st.write(trip.get("raw_input", "No description")[:200] + "...")

        st.caption(f"Trip ID: {trip['id']} | Created: {trip['created_at'][:10]}")
