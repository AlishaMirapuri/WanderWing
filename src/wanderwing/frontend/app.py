"""WanderWing — Travel companion matching.

Run: streamlit run src/wanderwing/frontend/app.py
"""

import streamlit as st
from wanderwing.frontend.utils.session import initialize_session_state
from wanderwing.frontend.utils.styling import apply_custom_css, render_section_header

st.set_page_config(
    page_title="WanderWing",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
apply_custom_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.markdown(
    '<div style="margin-bottom:2.5rem;">'
    '<div style="font-family:\'Syne\',sans-serif;font-size:1.3rem;'
    'font-weight:800;color:#1A1A2E;letter-spacing:-0.02em;'
    'line-height:1.2;margin-bottom:0.2rem;">WanderWing</div>'
    '<div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;'
    'letter-spacing:0.12em;color:rgba(26,26,46,0.28);">Travel companions</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Apply any pending programmatic navigation before the widget is instantiated.
if "_nav_target" in st.session_state:
    st.session_state["nav_page"] = st.session_state.pop("_nav_target")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Profile",
        "Trip",
        "Review",
        "Matches",
        "Activities",
        "Feedback",
        "Dashboard",
        "Evals",
    ],
    label_visibility="collapsed",
    key="nav_page",
)

# ── Page transition curtain ────────────────────────────────────────────────────
# `page` is embedded in the HTML comment so the inner DOM node is recreated on
# every navigation, triggering the ww-curtain fade-out CSS animation.
st.markdown(
    f'<!-- nav:{page} --><div class="ww-page-curtain"></div>',
    unsafe_allow_html=True,
)

# ── Home ──────────────────────────────────────────────────────────────────────

if page == "Home":
    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="ww-hero">'
        '<div class="ww-hero-tag">✦ Solo travel, reimagined</div>'
        '<h1 class="ww-display ww-anim ww-anim-1">'
        'Find your<br>'
        '<span style="background:linear-gradient(135deg,#FF6B6B 0%,#FFAB40 100%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">'
        'travel companion.</span>'
        '</h1>'
        '<p class="ww-anim ww-anim-2" style="font-size:1.15rem;max-width:520px;line-height:1.65;'
        'color:rgba(26,26,46,0.55);margin:1.25rem 0 0;">'
        'Describe your trip in plain English. We parse the intent, '
        'rank compatible travelers, and suggest what to do together.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("Get started →", type="primary"):
            st.session_state["_nav_target"] = "Profile"
            st.rerun()

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    # ── Stats strip ───────────────────────────────────────────────────────
    s1, s2, s3 = st.columns(3)
    for col, (val, label) in zip([s1, s2, s3], [
        ("15k+", "Travelers matched"),
        ("94%",  "Match satisfaction"),
        ("4.8★", "Average rating"),
    ]):
        with col:
            st.markdown(
                '<div class="ww-stat">'
                f'<span class="ww-stat-val">{val}</span>'
                f'<span class="ww-stat-label">{label}</span>'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    # ── Section header ─────────────────────────────────────────────────────
    render_section_header("How it works", "Three steps to your next trip.", num="→")

    # ── Step cards — middle card offset for asymmetry ─────────────────────
    c1, c2, c3 = st.columns(3)
    steps = [
        ("01", "Describe", "Write your trip plans in plain language — destination, dates, vibe."),
        ("02", "Match",    "Our hybrid ranker finds compatible travelers with overlapping trips."),
        ("03", "Connect",  "Get activity recommendations and a message to reach out."),
    ]
    for i, (col, (num, title, body)) in enumerate(zip([c1, c2, c3], steps)):
        mid_class = " ww-step-mid" if i == 1 else ""
        with col:
            st.markdown(
                f'<div class="ww-step-card ww-anim ww-anim-{i + 2}{mid_class}">'
                f'<span class="ww-step-ghost">{num}</span>'
                f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.12em;color:#FF6B6B;margin-bottom:0.6rem;">{num}</div>'
                f'<div style="font-size:1.05rem;font-weight:700;color:#1A1A2E;margin-bottom:0.5rem;">{title}</div>'
                f'<p style="font-size:0.875rem;line-height:1.6;margin:0;color:rgba(26,26,46,0.55);">{body}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<p style="font-size:0.75rem;color:rgba(26,26,46,0.25);margin-top:3rem;">'
        'Demo mode · mock data · no API key required</p>',
        unsafe_allow_html=True,
    )

elif page == "Profile":
    from wanderwing.frontend.views import create_profile
    create_profile.render()

elif page == "Trip":
    from wanderwing.frontend.views import describe_trip
    describe_trip.render()

elif page == "Review":
    from wanderwing.frontend.views import parsed_intent_review
    parsed_intent_review.render()

elif page == "Matches":
    from wanderwing.frontend.views import match_results
    match_results.render()

elif page == "Activities":
    from wanderwing.frontend.views import activity_recommendations
    activity_recommendations.render()

elif page == "Feedback":
    from wanderwing.frontend.views import feedback
    feedback.render()

elif page == "Dashboard":
    from wanderwing.frontend.views import experiment_dashboard
    experiment_dashboard.render()

elif page == "Evals":
    from wanderwing.frontend.views import prompt_eval_dashboard
    prompt_eval_dashboard.render()
