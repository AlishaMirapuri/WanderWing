"""Create Profile page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message
from wanderwing.frontend.utils.session import save_profile, get_profile, log_experiment_event


def render():
    """Render the Create Profile page."""
    render_page_header(
        "Create your profile.",
        "A few details so we can find the right match.",
        step="1 / 5",
    )

    profile = get_profile()

    with st.form("profile_form"):
        name = st.text_input(
            "Full name",
            value=profile.get("name", ""),
            placeholder="e.g., Jordan Rivera",
        )

        age_range = st.selectbox(
            "Age range",
            options=["", "Under 25", "25-34", "35-44", "45-54", "55+"],
            index=0 if not profile.get("age_range") else
                  ["", "Under 25", "25-34", "35-44", "45-54", "55+"].index(profile.get("age_range")),
        )

        email = st.text_input(
            "Email",
            value=profile.get("email", ""),
            placeholder="you@example.com",
        )

        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

        verification_level = st.slider(
            "Verification level",
            min_value=0,
            max_value=4,
            value=profile.get("verification_level", 0),
            help="0 = None · 1 = Email · 2 = Phone · 3 = ID · 4 = Video",
        )

        verification_labels = {
            0: "None",
            1: "Email verified",
            2: "Email + Phone",
            3: "Email + Phone + ID",
            4: "Full verification",
        }

        st.markdown(
            f'<div style="font-size:0.78rem;color:rgba(26,26,46,0.45);'
            f'font-weight:500;margin-bottom:1rem;">'
            f'Level {verification_level} — {verification_labels[verification_level]}</div>',
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button("Save profile", use_container_width=True, type="primary")

        if submitted:
            if not name or not age_range:
                st.error("Name and age range are required.")
            else:
                save_profile(name, age_range, email, verification_level)
                log_experiment_event(
                    "profile_completed",
                    {
                        "name": name,
                        "age_range": age_range,
                        "verification_level": verification_level,
                    },
                )
                render_success_message("Profile saved. Continue to describe your trip.")
                st.balloons()

    if profile.get("name"):
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        trust_pct = int(profile["trust_score"] * 100)
        st.markdown(
            '<div class="ww-card ww-anim">'
            '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:1rem;">Your profile</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">'
            '<div>'
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.08em;color:rgba(26,26,46,0.32);">Name</div>'
            f'<div style="font-size:1rem;font-weight:700;color:#1A1A2E;margin-top:0.25rem;">{profile["name"]}</div>'
            '</div>'
            '<div>'
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.08em;color:rgba(26,26,46,0.32);">Age range</div>'
            f'<div style="font-size:1rem;font-weight:700;color:#1A1A2E;margin-top:0.25rem;">{profile["age_range"]}</div>'
            '</div>'
            '<div>'
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.08em;color:rgba(26,26,46,0.32);">Verification</div>'
            f'<div style="font-size:1rem;font-weight:700;color:#1A1A2E;margin-top:0.25rem;">Level {profile["verification_level"]}</div>'
            '</div>'
            '<div>'
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.08em;color:rgba(26,26,46,0.32);">Trust score</div>'
            f'<div style="font-size:1rem;font-weight:700;color:#FF6B6B;margin-top:0.25rem;">{trust_pct}%</div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        col_nav, _ = st.columns([1, 2])
        with col_nav:
            if st.button("Continue to Trip →", type="primary", use_container_width=True):
                st.session_state["_nav_target"] = "Trip"
                st.rerun()
