"""Create Profile page."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_page_header, render_success_message
from wanderwing.frontend.utils.session import save_profile, get_profile


def render():
    """Render the Create Profile page."""
    render_page_header(
        "Create Your Profile",
        "Tell us about yourself to help us find compatible travel companions"
    )

    profile = get_profile()

    with st.form("profile_form"):
        st.markdown("### Basic Information")

        name = st.text_input(
            "Full Name",
            value=profile.get("name", ""),
            placeholder="e.g., Sarah Chen",
        )

        age_range = st.selectbox(
            "Age Range",
            options=["", "Under 25", "25-34", "35-44", "45-54", "55+"],
            index=0 if not profile.get("age_range") else
                  ["", "Under 25", "25-34", "35-44", "45-54", "55+"].index(profile.get("age_range")),
        )

        email = st.text_input(
            "Email",
            value=profile.get("email", ""),
            placeholder="sarah@example.com",
        )

        st.markdown("### Verification")
        st.markdown(
            """
            Higher verification levels increase match quality and trust.
            """
        )

        verification_level = st.slider(
            "Verification Level",
            min_value=0,
            max_value=4,
            value=profile.get("verification_level", 0),
            help="0=None, 1=Email, 2=Phone, 3=ID, 4=Video",
        )

        verification_labels = {
            0: "None",
            1: "Email Verified",
            2: "Email + Phone",
            3: "Email + Phone + ID",
            4: "Full Verification (Email + Phone + ID + Video)"
        }

        st.markdown(f"**Selected:** {verification_labels[verification_level]}")

        submitted = st.form_submit_button("Save Profile", use_container_width=True, type="primary")

        if submitted:
            if not name or not age_range:
                st.error("Please fill in Name and Age Range")
            else:
                save_profile(name, age_range, email, verification_level)
                render_success_message("Profile saved successfully!")
                st.balloons()

    if profile.get("name"):
        st.markdown("---")
        st.markdown("### Your Profile")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Age:** {profile['age_range']}")

        with col2:
            st.markdown(f"**Verification:** Level {profile['verification_level']}")
            trust_pct = int(profile['trust_score'] * 100)
            st.markdown(f"**Trust Score:** {trust_pct}%")

        st.markdown("---")
        st.info("✅ Profile complete! Continue to **Describe Trip** to find matches.")
