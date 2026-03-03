"""Match discovery page."""

import httpx
import streamlit as st

st.set_page_config(page_title="Discover Matches - WanderWing", page_icon="🔍", layout="wide")

st.title("🔍 Discover Travel Companions")

# Get API base URL from session state
api_base_url = st.session_state.get("api_base_url", "http://localhost:8000")
user_id = st.session_state.get("user_id", 1)

# Fetch user's trips
try:
    response = httpx.get(
        f"{api_base_url}/trips",
        headers={"X-User-Id": str(user_id)},
        timeout=10.0,
    )

    if response.status_code == 200:
        trips = response.json()

        if not trips:
            st.info("You haven't created any trips yet!")
            if st.button("Create Your First Trip"):
                st.switch_page("pages/1_create_trip.py")
        else:
            # Trip selector
            trip_options = {
                f"{trip['id']}: {trip['parsed_data']['destination'] if trip.get('parsed_data') else 'Unknown'}": trip[
                    "id"
                ]
                for trip in trips
            }

            selected_trip_label = st.selectbox(
                "Select a trip to find matches",
                options=list(trip_options.keys()),
            )

            selected_trip_id = trip_options[selected_trip_label]

            # Matching settings
            col1, col2 = st.columns([3, 1])
            with col1:
                min_score = st.slider(
                    "Minimum Match Score",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.1,
                    help="Only show matches above this compatibility score",
                )
            with col2:
                find_matches_btn = st.button("🔍 Find Matches", use_container_width=True)

            if find_matches_btn:
                with st.spinner("Finding compatible travelers..."):
                    try:
                        match_response = httpx.post(
                            f"{api_base_url}/matches/trips/{selected_trip_id}",
                            params={"min_score": min_score},
                            headers={"X-User-Id": str(user_id)},
                            timeout=60.0,
                        )

                        if match_response.status_code == 200:
                            matches = match_response.json()

                            if not matches:
                                st.warning("No matches found. Try lowering the minimum score or create more trips!")
                            else:
                                st.success(f"Found {len(matches)} compatible travelers!")

                                # Display matches
                                for match in matches:
                                    with st.container():
                                        st.divider()

                                        col1, col2 = st.columns([2, 1])

                                        with col1:
                                            st.subheader(
                                                f"🌍 {match['trip_2_destination']}"
                                            )
                                            st.write(f"**Traveler:** {match['trip_2_user_name']}")

                                            # Match score
                                            score = match["score"]["overall_score"]
                                            st.progress(score, text=f"Match Score: {score:.0%}")

                                            # Score breakdown
                                            with st.expander("Score Breakdown"):
                                                score_data = match["score"]
                                                st.metric("LLM Similarity", f"{score_data['llm_similarity']:.2f}")
                                                st.metric("Date Overlap", f"{score_data['date_overlap']:.2f}")
                                                st.metric(
                                                    "Activity Similarity",
                                                    f"{score_data['activity_similarity']:.2f}",
                                                )

                                        with col2:
                                            st.write("**Suggested Activities:**")
                                            for activity in match.get("suggested_activities", []):
                                                st.write(f"• {activity}")

                                            if st.button(
                                                "💬 Connect",
                                                key=f"connect_{match['id']}",
                                                use_container_width=True,
                                            ):
                                                st.success("Connection request sent! (Demo mode)")

                        else:
                            st.error(f"Failed to find matches: {match_response.text}")

                    except httpx.ConnectError:
                        st.error(f"Cannot connect to API server at {api_base_url}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    else:
        st.error(f"Failed to load trips: {response.text}")

except httpx.ConnectError:
    st.error(f"Cannot connect to API server. Make sure it's running at {api_base_url}")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Sidebar with tips
with st.sidebar:
    st.subheader("Matching Tips")
    st.markdown(
        """
        **How Matching Works:**

        - **Destination**: Must match exactly
        - **Dates**: More overlap = higher score
        - **Activities**: Common interests boost score
        - **Budget**: Similar tiers score higher

        **Match Score Components:**
        - 60% AI similarity analysis
        - 40% rule-based compatibility
        """
    )
