"""Reusable card components for WanderWing frontend."""

import streamlit as st
from wanderwing.frontend.utils.styling import render_tag, render_badge


def render_match_card(match_data: dict) -> None:
    """Render a match candidate card."""
    name = match_data.get("name", "Unknown")
    score = match_data.get("overall_score", 0.0)
    explanation = match_data.get("explanation", "")
    shared_activities = match_data.get("shared_activities", [])
    safety_flags = match_data.get("safety_flags", [])
    component_scores = match_data.get("component_scores", {})
    verification_level = match_data.get("verification_level", 0)
    trust_score = match_data.get("trust_score", 0.0)

    score_pct = int(score * 100)
    trust_pct = int(trust_score * 100)

    if score >= 0.75:
        pill_bg, pill_fg = "rgba(255,107,107,0.15)", "#FF6B6B"
    elif score >= 0.60:
        pill_bg, pill_fg = "rgba(26,26,46,0.08)", "rgba(26,26,46,0.70)"
    else:
        pill_bg, pill_fg = "rgba(26,26,46,0.05)", "rgba(26,26,46,0.40)"

    tags_html = "".join(
        '<span style="display:inline-block;background:rgba(26,26,46,0.06);'
        'color:rgba(26,26,46,0.60);padding:0.18rem 0.65rem;border-radius:100px;'
        'font-size:0.78rem;font-weight:500;margin:0.12rem 0.18rem 0.12rem 0;">'
        f'{a.replace("_", " ").title()}</span>'
        for a in shared_activities[:4]
    )

    safety_html = ""
    if safety_flags:
        safety_html = '<div style="margin-top:0.75rem;">' + "".join(
            '<span style="display:inline-block;background:rgba(255,107,107,0.12);'
            'color:#FF6B6B;padding:0.18rem 0.65rem;border-radius:100px;'
            f'font-size:0.78rem;font-weight:500;margin:0.12rem 0.18rem;">{f.replace("_", " ").title()}</span>'
            for f in safety_flags
        ) + "</div>"

    # Main card — no nested expandable HTML
    st.markdown(
        '<div class="ww-card ww-anim" style="position:relative;">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">'
        '<div>'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:1.45rem;'
        f'font-weight:700;color:#1A1A2E;letter-spacing:-0.02em;line-height:1.2;">{name}</div>'
        f'<div style="font-size:0.72rem;color:rgba(26,26,46,0.35);font-weight:500;'
        f'margin-top:0.2rem;letter-spacing:0.02em;">'
        f'Level {verification_level} verified&nbsp;&nbsp;·&nbsp;&nbsp;{trust_pct}% trust</div>'
        '</div>'
        f'<span style="display:inline-block;background:{pill_bg};color:{pill_fg};'
        f'padding:0.3rem 0.9rem;border-radius:100px;font-size:0.82rem;'
        f'font-weight:600;flex-shrink:0;margin-left:1rem;">{score_pct}%</span>'
        '</div>'
        f'<p style="font-size:0.9rem;color:rgba(26,26,46,0.55);line-height:1.65;margin:0 0 1rem;">{explanation}</p>'
        f'<div style="margin-bottom:0.25rem;">{tags_html}</div>'
        f'{safety_html}'
        '</div>',
        unsafe_allow_html=True,
    )

    # Compatibility breakdown as a native Streamlit expander
    with st.expander("Compatibility breakdown"):
        dims = [
            ("Destination",  component_scores.get("destination", 0)),
            ("Date overlap", component_scores.get("date_overlap", 0)),
            ("Activities",   component_scores.get("activity_similarity", 0)),
            ("Budget",       component_scores.get("budget_compatibility", 0)),
            ("Pace",         component_scores.get("pace_compatibility", 0)),
        ]
        for label, val in dims:
            pct = int(val * 100)
            bar_color = "#FF6B6B" if pct >= 75 else "rgba(26,26,46,0.20)"
            st.markdown(
                '<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">'
                f'<span style="width:80px;font-size:0.78rem;color:rgba(26,26,46,0.40);'
                f'font-weight:500;flex-shrink:0;">{label}</span>'
                '<div style="flex:1;background:rgba(26,26,46,0.07);border-radius:100px;height:4px;">'
                f'<div style="background:{bar_color};width:{pct}%;height:4px;border-radius:100px;"></div>'
                '</div>'
                f'<span style="width:28px;font-size:0.78rem;color:rgba(26,26,46,0.55);'
                f'font-weight:600;text-align:right;flex-shrink:0;">{pct}%</span>'
                '</div>',
                unsafe_allow_html=True,
            )


def render_activity_card(activity_data: dict) -> None:
    """Render an activity recommendation card."""
    name = activity_data.get("name", "Unknown Activity")
    description = activity_data.get("description", "")
    tags = activity_data.get("tags", [])
    cost = activity_data.get("cost", "")
    duration = activity_data.get("duration", "")
    score = activity_data.get("score", 0.0)
    shared_interests = activity_data.get("shared_interests", [])
    meeting_suggestion = activity_data.get("meeting_suggestion", "")

    score_pct = int(score * 100)
    if score >= 0.8:
        quality = "Excellent"
        pill_color = "rgba(255,107,107,0.15)"
        pill_text = "#FF6B6B"
    elif score >= 0.65:
        quality = "Good"
        pill_color = "rgba(26,26,46,0.07)"
        pill_text = "rgba(26,26,46,0.65)"
    else:
        quality = "Fair"
        pill_color = "rgba(26,26,46,0.05)"
        pill_text = "rgba(26,26,46,0.40)"

    tags_html = "".join(
        '<span style="display:inline-block;background:rgba(26,26,46,0.06);'
        'color:rgba(26,26,46,0.55);padding:0.18rem 0.65rem;border-radius:100px;'
        f'font-size:0.78rem;font-weight:500;margin:0.12rem 0.18rem 0.12rem 0;">{t.replace("-", " ").title()}</span>'
        for t in tags
    )

    meta_parts = []
    if cost:
        meta_parts.append(cost)
    if duration:
        meta_parts.append(duration)
    meta_html = (
        '<div style="font-size:0.8rem;color:rgba(26,26,46,0.38);font-weight:500;margin:0.6rem 0;">'
        + " · ".join(meta_parts) + "</div>"
    ) if meta_parts else ""

    interests_html = ""
    if shared_interests:
        interests_html = (
            '<div style="font-size:0.82rem;color:rgba(26,26,46,0.45);margin:0.6rem 0 0;">Both enjoy '
            '<span style="color:#1A1A2E;font-weight:600;">'
            + ", ".join(shared_interests) + "</span></div>"
        )

    # Main card body
    st.markdown(
        '<div class="ww-card ww-anim">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">'
        f'<div style="font-size:1.05rem;font-weight:700;color:#1A1A2E;letter-spacing:-0.01em;line-height:1.3;">{name}</div>'
        f'<span style="display:inline-block;background:{pill_color};color:{pill_text};'
        f'padding:0.22rem 0.75rem;border-radius:100px;font-size:0.78rem;'
        f'font-weight:600;flex-shrink:0;margin-left:1rem;">{quality}</span>'
        '</div>'
        f'<p style="font-size:0.9rem;color:rgba(26,26,46,0.55);line-height:1.65;margin:0;">{description}</p>'
        f'{meta_html}'
        f'<div>{tags_html}</div>'
        f'{interests_html}'
        '</div>',
        unsafe_allow_html=True,
    )

    # Suggested message rendered separately to avoid markdown code-block interpretation
    st.markdown(
        '<div style="background:rgba(255,171,64,0.06);border-radius:14px;'
        'padding:1rem 1.25rem;margin-top:0.25rem;margin-bottom:0.5rem;">'
        '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.4rem;">Suggested message</div>'
        f'<p style="font-size:0.88rem;color:rgba(26,26,46,0.60);margin:0;'
        f'font-style:italic;line-height:1.6;">\u201c{meeting_suggestion}\u201d</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_intent_comparison(raw_text: str, parsed_intent: dict) -> None:
    """Side-by-side: raw text \u2194 parsed intent."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">Your words</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:rgba(255,255,255,0.90);padding:1.5rem;border-radius:24px;'
            'border:1px solid rgba(255,107,107,0.10);min-height:260px;">'
            f'<p style="color:rgba(26,26,46,0.65);line-height:1.75;white-space:pre-wrap;'
            f'font-size:0.9rem;margin:0;">{raw_text}</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with col2:
        destination = parsed_intent.get("primary_destination", "\u2014")
        start_date  = parsed_intent.get("overall_start_date", "\u2014")
        end_date    = parsed_intent.get("overall_end_date", "\u2014")
        duration    = parsed_intent.get("duration_days", "\u2014")
        activities  = parsed_intent.get("activities", [])
        budget      = parsed_intent.get("budget_tier", "\u2014").replace("_", " ").title()
        pace        = parsed_intent.get("pace_preference", "\u2014").replace("_", " ").title()
        confidence  = parsed_intent.get("confidence_score", 0.0)
        conf_pct    = int(confidence * 100)

        acts_html = "".join(
            '<span style="display:inline-block;background:rgba(255,107,107,0.12);'
            'color:#FF6B6B;padding:0.15rem 0.6rem;border-radius:100px;'
            f'font-size:0.78rem;font-weight:500;margin:0.12rem 0.15rem;">{a.replace("_", " ").title()}</span>'
            for a in activities
        ) or "\u2014"

        rows = [
            ("Destination", f"<strong style='color:#1A1A2E;'>{destination}</strong>"),
            ("Dates",       f"{start_date} \u2192 {end_date}"),
            ("Duration",    f"{duration} days"),
            ("Activities",  acts_html),
            ("Budget",      budget),
            ("Pace",        pace),
        ]
        rows_html = "".join(
            '<tr>'
            f'<td style="padding:0.45rem 0.75rem 0.45rem 0;font-size:0.68rem;font-weight:600;'
            f'text-transform:uppercase;letter-spacing:0.09em;color:rgba(26,26,46,0.32);'
            f'white-space:nowrap;vertical-align:top;">{lbl}</td>'
            f'<td style="padding:0.45rem 0;font-size:0.88rem;color:rgba(26,26,46,0.65);">{val}</td>'
            '</tr>'
            for lbl, val in rows
        )

        if conf_pct >= 80:
            conf_bg, conf_fg = "#FF6B6B", "#FFFFFF"
        else:
            conf_bg, conf_fg = "rgba(26,26,46,0.08)", "rgba(26,26,46,0.62)"

        st.markdown(
            '<div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.10em;color:rgba(26,26,46,0.32);margin-bottom:0.75rem;">What we extracted</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:rgba(255,255,255,0.90);padding:1.5rem;border-radius:24px;'
            'border:1px solid rgba(255,107,107,0.10);min-height:260px;">'
            f'<table style="width:100%;border-collapse:collapse;">{rows_html}</table>'
            '<div style="margin-top:1rem;display:flex;align-items:center;gap:0.6rem;">'
            '<span style="font-size:0.68rem;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.09em;color:rgba(26,26,46,0.32);">Confidence</span>'
            f'<span style="background:{conf_bg};color:{conf_fg};font-weight:600;'
            f'font-size:0.78rem;padding:0.18rem 0.65rem;border-radius:100px;">{conf_pct}%</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
