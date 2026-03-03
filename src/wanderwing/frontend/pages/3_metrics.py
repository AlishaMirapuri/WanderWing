"""Metrics and analytics dashboard."""

import streamlit as st

st.set_page_config(page_title="Metrics - WanderWing", page_icon="📊", layout="wide")

st.title("📊 Platform Metrics")
st.markdown("Analytics and insights (Demo - will be populated with real data)")

# Placeholder metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Trips", "127", delta="12")

with col2:
    st.metric("Matches Created", "89", delta="8")

with col3:
    st.metric("Avg Match Score", "0.72", delta="0.05")

with col4:
    st.metric("Connection Rate", "34%", delta="3%")

st.divider()

# Tabs for different metrics
tab1, tab2, tab3 = st.tabs(["Match Quality", "User Engagement", "Experiments"])

with tab1:
    st.subheader("Match Quality Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Match Score Distribution**")
        st.info("Chart: Distribution of match scores (to be implemented)")

        st.markdown("**Top Destinations**")
        destinations = [
            ("Tokyo", 23),
            ("Paris", 18),
            ("Bali", 15),
            ("Barcelona", 12),
            ("Bangkok", 10),
        ]
        for dest, count in destinations:
            st.write(f"- {dest}: {count} trips")

    with col2:
        st.markdown("**User Feedback**")
        st.metric("Avg Rating", "4.2 / 5.0")
        st.metric("Total Ratings", "67")

        st.markdown("**Conversion Funnel**")
        st.write("- Trips created: 100%")
        st.write("- Matches found: 70%")
        st.write("- Connections sent: 34%")
        st.write("- Connections accepted: 18%")

with tab2:
    st.subheader("User Engagement")

    st.markdown("**Activity Timeline**")
    st.info("Chart: User activity over time (to be implemented)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Trip Creation Rate**")
        st.metric("Trips per User", "1.8")
        st.metric("Active Users", "71")

    with col2:
        st.markdown("**Match Engagement**")
        st.metric("Matches Viewed", "234")
        st.metric("Avg Matches per Trip", "7.2")

with tab3:
    st.subheader("A/B Experiments")

    st.markdown("**Active Experiments**")

    # Experiment 1
    with st.expander("Itinerary Extraction Prompt (v1 vs v2)", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Variant 1 (Control)**")
            st.metric("Users", "35")
            st.metric("Success Rate", "87%")
            st.metric("Avg Confidence", "0.81")

        with col2:
            st.write("**Variant 2 (Test)**")
            st.metric("Users", "36")
            st.metric("Success Rate", "92%", delta="5%")
            st.metric("Avg Confidence", "0.85", delta="0.04")

    # Experiment 2
    with st.expander("Matching Algorithm (Hybrid vs LLM-only)"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Hybrid (Control)**")
            st.metric("Matches", "42")
            st.metric("Acceptance Rate", "38%")
            st.metric("Avg Processing Time", "1.2s")

        with col2:
            st.write("**LLM-Only (Test)**")
            st.metric("Matches", "47")
            st.metric("Acceptance Rate", "41%", delta="3%")
            st.metric("Avg Processing Time", "2.8s", delta="1.6s")

# Sidebar with refresh
with st.sidebar:
    st.subheader("Dashboard Controls")

    if st.button("🔄 Refresh Metrics"):
        st.rerun()

    st.divider()

    st.markdown("**Data Range**")
    st.date_input("From", value=None)
    st.date_input("To", value=None)

    st.divider()

    st.markdown("**Export**")
    if st.button("📥 Download CSV"):
        st.info("Export feature coming soon")
