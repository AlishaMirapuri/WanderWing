"""
Reusable card components for WanderWing frontend.

Provides match cards, activity cards, and other UI components.
"""

import streamlit as st
from wanderwing.frontend.utils.styling import render_tag, render_badge


def render_match_card(match_data):
    """
    Render a match candidate card.

    Args:
        match_data: Dict with match information
    """
    name = match_data.get("name", "Unknown")
    score = match_data.get("overall_score", 0.0)
    explanation = match_data.get("explanation", "")
    shared_activities = match_data.get("shared_activities", [])
    safety_flags = match_data.get("safety_flags", [])
    component_scores = match_data.get("component_scores", {})
    verification_level = match_data.get("verification_level", 0)
    trust_score = match_data.get("trust_score", 0.0)

    # Determine score category
    if score >= 0.75:
        score_badge = render_badge(f"{int(score * 100)}% Match", "high")
        score_color = "#10B981"
    elif score >= 0.60:
        score_badge = render_badge(f"{int(score * 100)}% Match", "medium")
        score_color = "#F59E0B"
    else:
        score_badge = render_badge(f"{int(score * 100)}% Match", "low")
        score_color = "#EF4444"

    # Build tags
    tags_html = "".join([render_tag(act.replace("_", " ").title(), "info") for act in shared_activities[:3]])

    # Safety flags
    safety_html = ""
    if safety_flags:
        safety_html = "".join([render_tag(f"⚠️ {flag.replace('_', ' ').title()}", "warning") for flag in safety_flags])

    # Verification badges
    verification_stars = "⭐" * verification_level
    trust_percent = int(trust_score * 100)

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #EEF2FF 0%, #DBEAFE 100%);
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                    border: 2px solid {score_color};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0; color: #1F2937; font-size: 1.5rem;">{name}</h3>
                    <p style="margin: 0.25rem 0; color: #6B7280; font-size: 0.9rem;">
                        {verification_stars} Level {verification_level} • Trust Score: {trust_percent}%
                    </p>
                </div>
                <div style="text-align: right;">
                    {score_badge}
                </div>
            </div>

            <p style="color: #374151; margin: 1rem 0;">{explanation}</p>

            <div style="margin: 1rem 0;">
                <strong style="color: #1F2937;">Shared Interests:</strong><br>
                {tags_html}
            </div>

            {f'<div style="margin: 1rem 0;">{safety_html}</div>' if safety_html else ''}

            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: #2563EB; font-weight: 600;">
                    View Compatibility Breakdown
                </summary>
                <div style="margin-top: 0.75rem; padding: 0.75rem; background: white; border-radius: 8px;">
                    <table style="width: 100%; font-size: 0.9rem;">
                        <tr>
                            <td style="padding: 0.25rem 0;">Destination:</td>
                            <td style="text-align: right; font-weight: 600;">{int(component_scores.get('destination', 0) * 100)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 0.25rem 0;">Date Overlap:</td>
                            <td style="text-align: right; font-weight: 600;">{int(component_scores.get('date_overlap', 0) * 100)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 0.25rem 0;">Activity Match:</td>
                            <td style="text-align: right; font-weight: 600;">{int(component_scores.get('activity_similarity', 0) * 100)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 0.25rem 0;">Budget:</td>
                            <td style="text-align: right; font-weight: 600;">{int(component_scores.get('budget_compatibility', 0) * 100)}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 0.25rem 0;">Pace:</td>
                            <td style="text-align: right; font-weight: 600;">{int(component_scores.get('pace_compatibility', 0) * 100)}%</td>
                        </tr>
                    </table>
                </div>
            </details>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_activity_card(activity_data):
    """
    Render an activity recommendation card.

    Args:
        activity_data: Dict with activity information
    """
    name = activity_data.get("name", "Unknown Activity")
    description = activity_data.get("description", "")
    tags = activity_data.get("tags", [])
    cost = activity_data.get("cost", "")
    duration = activity_data.get("duration", "")
    score = activity_data.get("score", 0.0)
    shared_interests = activity_data.get("shared_interests", [])
    meeting_suggestion = activity_data.get("meeting_suggestion", "")

    # Score indicator
    score_percent = int(score * 100)
    if score >= 0.8:
        score_color = "#10B981"
        score_label = "Excellent Match"
    elif score >= 0.65:
        score_color = "#3B82F6"
        score_label = "Good Match"
    else:
        score_color = "#6B7280"
        score_label = "Fair Match"

    # Build tags
    tags_html = "".join([render_tag(tag.replace("-", " ").title()) for tag in tags])

    # Shared interests
    interests_html = ""
    if shared_interests:
        interests_html = f"""
        <div style="margin: 0.75rem 0;">
            <strong style="color: #1F2937; font-size: 0.9rem;">Why this matches:</strong>
            <p style="color: #6B7280; font-size: 0.9rem; margin: 0.25rem 0;">
                Both interested in {', '.join(shared_interests)}
            </p>
        </div>
        """

    st.markdown(
        f"""
        <div style="background: white; border-radius: 12px; padding: 1.25rem;
                    margin-bottom: 1rem; border: 1px solid #E5E7EB;
                    transition: transform 0.2s;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                <h3 style="margin: 0; color: #1F2937; font-size: 1.25rem;">{name}</h3>
                <span style="background: {score_color}; color: white; padding: 0.25rem 0.75rem;
                             border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                    {score_label}
                </span>
            </div>

            <p style="color: #6B7280; font-size: 0.95rem; margin: 0.5rem 0;">{description}</p>

            <div style="display: flex; gap: 1.5rem; margin: 0.75rem 0; font-size: 0.9rem;">
                <span style="color: #6B7280;">💰 {cost}</span>
                <span style="color: #6B7280;">⏱️ {duration}</span>
            </div>

            <div style="margin: 0.75rem 0;">
                {tags_html}
            </div>

            {interests_html}

            <div style="background: #F9FAFB; padding: 1rem; border-radius: 8px;
                        border-left: 3px solid #3B82F6; margin-top: 1rem;">
                <strong style="color: #1F2937; font-size: 0.9rem;">💬 Suggested Message:</strong>
                <p style="color: #4B5563; font-size: 0.9rem; margin: 0.5rem 0 0 0; font-style: italic;">
                    "{meeting_suggestion}"
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_intent_comparison(raw_text, parsed_intent):
    """
    Render side-by-side comparison of raw text and parsed intent.

    Args:
        raw_text: Original user input
        parsed_intent: Structured parsed data
    """
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 Your Description")
        st.markdown(
            f"""
            <div style="background: #F9FAFB; padding: 1rem; border-radius: 8px;
                        min-height: 300px; border: 1px solid #E5E7EB;">
                <p style="color: #374151; line-height: 1.6; white-space: pre-wrap;">{raw_text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### 🤖 Parsed Intent")

        # Format parsed intent nicely
        destination = parsed_intent.get("primary_destination", "N/A")
        start_date = parsed_intent.get("overall_start_date", "N/A")
        end_date = parsed_intent.get("overall_end_date", "N/A")
        duration = parsed_intent.get("duration_days", "N/A")
        activities = parsed_intent.get("activities", [])
        budget = parsed_intent.get("budget_tier", "N/A")
        pace = parsed_intent.get("pace_preference", "N/A")
        confidence = parsed_intent.get("confidence_score", 0.0)

        activities_list = "".join([f"<li>{act.replace('_', ' ').title()}</li>" for act in activities])

        st.markdown(
            f"""
            <div style="background: #EEF2FF; padding: 1rem; border-radius: 8px;
                        min-height: 300px; border: 2px solid #3B82F6;">
                <table style="width: 100%; font-size: 0.95rem;">
                    <tr>
                        <td style="padding: 0.5rem 0; color: #6B7280; font-weight: 600;">Destination:</td>
                        <td style="padding: 0.5rem 0; color: #1F2937;">{destination}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0; color: #6B7280; font-weight: 600;">Dates:</td>
                        <td style="padding: 0.5rem 0; color: #1F2937;">{start_date} to {end_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0; color: #6B7280; font-weight: 600;">Duration:</td>
                        <td style="padding: 0.5rem 0; color: #1F2937;">{duration} days</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0; color: #6B7280; font-weight: 600; vertical-align: top;">Activities:</td>
                        <td style="padding: 0.5rem 0; color: #1F2937;">
                            <ul style="margin: 0; padding-left: 1.25rem;">
                                {activities_list}
                            </ul>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0; color: #6B7280; font-weight: 600;">Budget:</td>
                        <td style="padding: 0.5rem 0; color: #1F2937;">{budget.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.5rem 0; color: #6B7280; font-weight: 600;">Pace:</td>
                        <td style="padding: 0.5rem 0; color: #1F2937;">{pace.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <td colspan="2" style="padding-top: 1rem;">
                            <div style="background: white; padding: 0.5rem; border-radius: 6px; text-align: center;">
                                <span style="color: #6B7280; font-size: 0.85rem;">Confidence:</span>
                                <span style="color: #10B981; font-weight: 700; font-size: 1.1rem; margin-left: 0.5rem;">
                                    {int(confidence * 100)}%
                                </span>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
