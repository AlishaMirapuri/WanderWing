"""
Session state management for WanderWing frontend.

Manages user data across page navigation and wires experiment event logging.
"""

import uuid
from datetime import datetime

import streamlit as st


def _get_event_logger():
    """Lazy import of event_logger to avoid import errors if DB not available."""
    try:
        from wanderwing.core.event_logger import event_logger
        return event_logger
    except Exception:
        return None


def initialize_session_state():
    """Initialize session state with default values."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True

        # Stable user identifier for this browser session
        st.session_state.user_id = str(uuid.uuid4())

        # Deterministic variant assignment
        logger = _get_event_logger()
        if logger:
            st.session_state.experiment_variant = logger.assign_variant(
                st.session_state.user_id
            )
        else:
            st.session_state.experiment_variant = "variant_a"

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

        # Interaction log (in-session copy)
        st.session_state.interaction_log = []

        # Track whether user has already parsed once (for parse_edited detection)
        st.session_state.parse_count = 0

        # ── Seed demo data so Matches / Activities are immediately populated ──
        _seed_demo_data()


def log_experiment_event(event_type: str, metadata: dict | None = None) -> None:
    """
    Log one experiment event to the database.

    Silently swallows errors so a DB failure never breaks the UI flow.
    """
    try:
        logger = _get_event_logger()
        if logger is None:
            return
        user_id = st.session_state.get("user_id", "unknown")
        variant = st.session_state.get("experiment_variant", "variant_a")
        logger.log(user_id, variant, event_type, metadata or {})

        # Also keep an in-session copy for debugging
        st.session_state.interaction_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "variant": variant,
                "data": metadata or {},
            }
        )
    except Exception:
        pass


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
    """Legacy helper — prefer log_experiment_event()."""
    log_experiment_event(event_type, data)


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


def _seed_demo_data():
    """Pre-populate session with a demo user journey for immediate exploration."""
    from wanderwing.frontend.utils.mock_data import (
        generate_parsed_intent,
        generate_mock_matches,
        generate_mock_activities,
    )

    # Demo profile
    st.session_state.profile = {
        "name": "Jordan Rivera",
        "age_range": "25-34",
        "email": "jordan@example.com",
        "verification_level": 3,
        "trust_score": 0.95,
    }

    # Demo trip
    trip_text = (
        "I'm heading to Barcelona from June 15–25. "
        "Big foodie — want to do tapas tours and local markets. "
        "Also love hiking, so maybe Montserrat for a day. "
        "Moderate budget, relaxed pace."
    )
    st.session_state.trip_text = trip_text

    parsed_intent = generate_parsed_intent(trip_text)
    st.session_state.parsed_intent = parsed_intent

    # Demo matches
    profile = st.session_state.profile
    matches = generate_mock_matches(profile, parsed_intent, num_matches=5)
    st.session_state.matches = matches

    # Pre-select the top match and generate activities
    if matches:
        top_match = matches[0]
        st.session_state.selected_match = top_match
        activities = generate_mock_activities(top_match, parsed_intent, num_activities=5)
        st.session_state.activities = activities
