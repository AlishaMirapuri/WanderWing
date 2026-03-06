"""
Experiment registry for WanderWing UX flow A/B/C test.

This module defines the active experiments and documents the hypotheses being tested.
It is the single source of truth for experiment configuration.

--- FOR PMs / FDEs / INTERVIEW PANELS ---

## Experiment: ux_flow (3-variant A/B/C test)

### What we're testing
The UX shown to users after their trip description is parsed and before they see matches.
Specifically: how much context/confirmation to show before surfacing match results.

### Variants

**Variant A (40% traffic) — "Structured Preview"**
- Shows a full itinerary summary card before the intent comparison view
- Hypothesis: Displaying structured trip data builds confidence that the AI understood
  the user correctly, reducing the rate of users going back to re-parse (parse_correction_rate)
  and increasing end-to-end completion.
- Expected to win on: parse_correction_rate, completion_rate
- Risk: More steps → potential drop-off before reaching matches

**Variant B (40% traffic) — "Fast to Matches"**
- Replaces the full comparison view with a single-line summary ("We understood: Tokyo · Apr 1–10")
- Shows one large "Find My Matches" CTA immediately, no Edit button
- Hypothesis: Reducing friction to the matching step increases match clickthrough rate,
  even if some users have less confidence their intent was captured accurately.
- Expected to win on: match_clickthrough_rate (higher CTR due to reduced friction)
- Risk: Lower intent accuracy → worse match quality → lower downstream satisfaction

**Variant C (20% traffic) — "Explainable Matching"**
- Shows the full itinerary summary (like A) + a preview of top 2 match archetypes
- e.g., "You'll likely match with adventure-minded solo travelers"
- Hypothesis: Showing match explanations and activity previews upfront increases
  recommendation satisfaction and final feedback submission rate. Users who understand
  why they're matched are more likely to convert.
- Expected to win on: recommendation_satisfaction, completion_rate
- 20% traffic: riskier, more experimental — lower sample size acceptable initially

### Key PM questions this experiment answers
1. Does Variant B's higher CTR come at the cost of match quality or satisfaction?
2. Does Variant C's richer UI justify the 20% traffic share given its heavier render cost?
3. Is parse_correction_rate a good proxy for intent understanding quality?
4. What is the minimum sample size per variant for statistical significance?
   (Rule of thumb: ~400 users per variant for 80% power at 5% significance)

### Success criteria (launch bar to ship a variant)
- completion_rate: target > 50% (feedback_submitted / profile_completed)
- match_clickthrough_rate: target > 70% (match_clicked / parse_accepted)
- recommendation_satisfaction: target > 0.6 (mean thumbs-up rating)
- parse_correction_rate: target < 15% (lower = better intent accuracy)

### Guardrails (ship only if these are NOT violated)
- No variant should have completion_rate < 30% (indicates UX confusion)
- No variant should have parse_correction_rate > 35% (indicates poor intent capture)

### How to read results in the dashboard
- Navigate to the 📊 Dashboard page in the Streamlit app
- The funnel chart shows drop-off at each event step per variant
- The metric table shows all 4 key metrics side-by-side
"""

class ExperimentConfig:
    """Lightweight experiment config — mirrors wanderwing.core.experiments.ExperimentConfig."""

    def __init__(self, name: str, variants: dict[str, float]) -> None:
        self.name = name
        self.variants = variants


# The active UX flow experiment.
# Traffic weights must sum to 1.0.
UX_FLOW_EXPERIMENT = ExperimentConfig(
    name="ux_flow",
    variants={
        "variant_a": 0.40,  # Structured Preview — show full itinerary summary card
        "variant_b": 0.40,  # Fast to Matches — one-liner + immediate CTA
        "variant_c": 0.20,  # Explainable Matching — summary + match archetype preview
    },
)

# Registry of all active experiments.
# Add new experiments here as the product grows.
EXPERIMENT_REGISTRY: dict[str, ExperimentConfig] = {
    UX_FLOW_EXPERIMENT.name: UX_FLOW_EXPERIMENT,
}
