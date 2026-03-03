"""Trip creation page."""

import httpx
import streamlit as st

st.set_page_config(page_title="Create Trip - WanderWing", page_icon="✈️", layout="wide")

st.title("📝 Create Your Trip")
st.markdown("Describe your travel plans in natural language. Our AI will understand your preferences!")

# Get API base URL from session state
api_base_url = st.session_state.get("api_base_url", "http://localhost:8000")
user_id = st.session_state.get("user_id", 1)

# Trip input form
with st.form("trip_form"):
    st.subheader("Tell us about your trip")

    trip_description = st.text_area(
        "Trip Description",
        placeholder="Example: I'm going to Tokyo for 10 days in April. Love hiking, trying local food, and visiting temples. Looking for budget-friendly options and would enjoy meeting other solo travelers.",
        height=150,
        help="Describe your destination, dates, interests, and travel style in your own words",
    )

    submit_button = st.form_submit_button("Create Trip", use_container_width=True)

if submit_button:
    if not trip_description.strip():
        st.error("Please describe your trip!")
    else:
        with st.spinner("Extracting itinerary with AI..."):
            try:
                # Call API to create trip
                response = httpx.post(
                    f"{api_base_url}/trips",
                    json={"raw_input": trip_description},
                    headers={"X-User-Id": str(user_id)},
                    timeout=30.0,
                )

                if response.status_code == 201:
                    trip_data = response.json()
                    st.success("✅ Trip created successfully!")

                    # Display parsed itinerary
                    if trip_data.get("parsed_data"):
                        st.subheader("Parsed Itinerary")

                        parsed = trip_data["parsed_data"]

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("Destination", parsed.get("destination", "Unknown"))
                            if parsed.get("start_date") and parsed.get("end_date"):
                                st.metric(
                                    "Dates",
                                    f"{parsed['start_date']} to {parsed['end_date']}",
                                )
                            if parsed.get("duration_days"):
                                st.metric("Duration", f"{parsed['duration_days']} days")

                        with col2:
                            st.metric("Budget Tier", parsed.get("budget_tier", "Unknown").title())
                            if parsed.get("activities"):
                                st.write("**Activities:**")
                                for activity in parsed["activities"]:
                                    st.write(f"- {activity.replace('_', ' ').title()}")

                        # Confidence score
                        confidence = parsed.get("confidence_score", 0)
                        st.progress(confidence, text=f"Confidence: {confidence:.0%}")

                        # Ambiguities
                        if parsed.get("ambiguities"):
                            st.warning("**Needs Clarification:**")
                            for ambiguity in parsed["ambiguities"]:
                                st.write(f"- {ambiguity}")

                        # Store trip ID for later use
                        st.session_state.last_trip_id = trip_data["id"]

                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔍 Find Matches", use_container_width=True):
                                st.switch_page("pages/2_discover_matches.py")
                        with col2:
                            if st.button("📝 Create Another Trip", use_container_width=True):
                                st.rerun()

                    else:
                        st.warning("Trip created but itinerary extraction failed. You can still find matches!")

                else:
                    st.error(f"Failed to create trip: {response.text}")

            except httpx.ConnectError:
                st.error(
                    "❌ Cannot connect to API server. Make sure it's running at "
                    f"{api_base_url}"
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Sidebar with examples
with st.sidebar:
    st.subheader("Example Trip Descriptions")

    examples = [
        "Planning a 2-week backpacking trip through Southeast Asia starting in Bangkok. Love street food and temples!",
        "Going to Paris for 5 days next month. Interested in art museums, cafes, and photography.",
        "Weekend trip to LA in March. Want to hit the beach, try good restaurants, budget-friendly.",
        "Month-long digital nomad stay in Lisbon. Looking for coworking spaces and local experiences.",
    ]

    for i, example in enumerate(examples, 1):
        with st.expander(f"Example {i}"):
            st.write(example)
            if st.button(f"Use This", key=f"example_{i}"):
                st.session_state.trip_example = example
                st.rerun()

    if "trip_example" in st.session_state:
        trip_description = st.session_state.trip_example
        del st.session_state.trip_example
