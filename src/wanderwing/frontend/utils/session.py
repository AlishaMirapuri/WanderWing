"""
Session state management for WanderWing frontend.

Manages user data across page navigation.
"""

import streamlit as st
from datetime import datetime, timedelta


def initialize_session_state():
    """Initialize session state with default values."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True

        # User profile
        st.session_state.profile = {
            "name": "",
            "age_range": "",
            "email": "",
            "verification_level": 0,
            "trust_score": 0.5,
        }

        # Trip description (raw text)
        st.session_state.trip_text = ""

        # Parsed intent
        st.session_state.parsed_intent = None

        # Match results
        st.session_state.matches = []

        # Selected match for activities
        st.session_state.selected_match = None

        # Activity recommendations
        st.session_state.activities = []

        # Feedback
        st.session_state.feedback = {}

        # Experiment tracking
        st.session_state.experiment_variant = "variant_a"
        st.session_state.interaction_log = []


def save_profile(name, age_range, email, verification_level):
    """Save profile data to session state."""
    st.session_state.profile = {
        "name": name,
        "age_range": age_range,
        "email": email,
        "verification_level": verification_level,
        "trust_score": min(1.0, 0.5 + (verification_level * 0.15)),
    }


def save_trip_description(text):
    """Save trip description to session state."""
    st.session_state.trip_text = text


def save_parsed_intent(intent):
    """Save parsed intent to session state."""
    st.session_state.parsed_intent = intent


def save_matches(matches):
    """Save match results to session state."""
    st.session_state.matches = matches


def select_match(match):
    """Select a match for activity recommendations."""
    st.session_state.selected_match = match


def save_activities(activities):
    """Save activity recommendations to session state."""
    st.session_state.activities = activities


def save_feedback(match_id, rating, comments, accepted):
    """Save user feedback to session state."""
    feedback_entry = {
        "match_id": match_id,
        "rating": rating,
        "comments": comments,
        "accepted": accepted,
        "timestamp": datetime.now(),
        "variant": st.session_state.experiment_variant,
    }

    if "feedback_history" not in st.session_state:
        st.session_state.feedback_history = []

    st.session_state.feedback_history.append(feedback_entry)
    st.session_state.feedback = feedback_entry


def log_interaction(event_type, data):
    """Log user interaction for experiment tracking."""
    interaction = {
        "timestamp": datetime.now(),
        "event_type": event_type,
        "variant": st.session_state.experiment_variant,
        "data": data,
    }
    st.session_state.interaction_log.append(interaction)


def get_profile():
    """Get current profile data."""
    return st.session_state.get("profile", {})


def get_trip_text():
    """Get trip description text."""
    return st.session_state.get("trip_text", "")


def get_parsed_intent():
    """Get parsed intent."""
    return st.session_state.get("parsed_intent")


def get_matches():
    """Get match results."""
    return st.session_state.get("matches", [])


def get_selected_match():
    """Get selected match."""
    return st.session_state.get("selected_match")


def get_activities():
    """Get activity recommendations."""
    return st.session_state.get("activities", [])


def get_feedback():
    """Get feedback data."""
    return st.session_state.get("feedback", {})


def is_profile_complete():
    """Check if profile is complete."""
    profile = get_profile()
    return bool(profile.get("name") and profile.get("age_range"))


def is_trip_described():
    """Check if trip is described."""
    return bool(get_trip_text())


def is_intent_parsed():
    """Check if intent is parsed."""
    return get_parsed_intent() is not None


def has_matches():
    """Check if matches exist."""
    return len(get_matches()) > 0


def has_activities():
    """Check if activities exist."""
    return len(get_activities()) > 0
