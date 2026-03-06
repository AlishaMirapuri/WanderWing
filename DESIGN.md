# WanderWing — Design Process

> A first-person account of how I designed the frontend: what I built, why, how I evaluated it, and what I'd change.

---

## TL;DR

I started with a bare Streamlit app and no visual identity. Over several iterations I built a custom design system ("Gradient Drift"), added a motion layer, did a full consistency audit, ran a product-designer QA pass, and fixed every broken navigation flow. The result is a cohesive, warm, animated UI that works within Streamlit's constraints. The biggest recurring tension was *playful vs. restrained* — I kept pulling things back after each pass.

---

## How I Worked

I used an iterative, prompt-driven design loop:

1. **Build the visual system** — defined tokens (color, type, radius, shadow) as CSS injected via `st.markdown()`
2. **Add personality** — hero layout, ghost numbers, step cards, stat strip
3. **Add motion** — page transitions, skeleton loading, empty states
4. **Consistency audit** — found and fixed ~49 issues across 12 categories
5. **QA punchlist** — wrote 20 specific issues as a product designer, implemented top 5
6. **Navigation audit** — fixed every dead-end button

Each phase ended with a visual check and a decision about what to push further vs. pull back.

---

## Design Principles

These four principles guided every decision:

**1. Warm, not sterile.**
Most travel apps default to cold whites and blues. I chose a warm off-white base (`#FFFBF5`) and a coral-amber-sky accent palette to feel inviting rather than clinical.

**2. Motion communicates, not decorates.**
Every animation has a reason: the page curtain signals a context switch, the skeleton tells you something is loading, the compass float makes an empty state feel alive rather than broken. I actively cut animations that were just visual noise.

**3. Progressive disclosure.**
The flow is gated: you can't reach Review without a trip description, you can't see Matches without a parsed intent. Each page shows only what's needed at that step. The sidebar always shows all pages so power users can jump freely.

**4. Playful but restrained.**
After every "add more personality" pass, I immediately followed with a "pull it back" audit. The tilt on card hover went from `-0.6deg` to `-0.3deg`. The fade-up blur went from `3px` to `1.5px`. The feature blob opacity went from `0.22` to `0.12`. The final tone is warm and slightly expressive — not a design portfolio piece fighting for attention.

---

## Visual System — "Gradient Drift"

### Color Tokens

| Name | Hex | Use |
|------|-----|-----|
| Sunrise | `#FF6B6B` | Primary actions, accents, data highlights |
| Amber | `#FFAB40` | Secondary warmth, gradient endpoint, shimmer |
| Sky | `#6EC6FF` | Tertiary accent, background blobs |
| Base | `#FFFBF5` | Page background — warm off-white |
| Ink | `#1A1A2E` | All text, deep navy tint |

The primary button uses a 3-stop gradient (`#FF6B6B → #FFAB40 → #FF6B6B`) with `background-size: 220%` so hovering shifts the color band — a subtle movement without any JS.

### Typography

- **Display / headings**: Syne 800 — geometric, high-contrast, opinionated
- **Body**: Inter 300–700 — neutral, legible, system-friendly
- **Labels / eyebrows**: Inter 600, uppercase, `letter-spacing: 0.10em` — establishes hierarchy without extra size

### Radius Scale

`8px` (inputs) → `14px` (tags, badges) → `24px` (comparison panels) → `32px` (hero card) → `100px` (pills)

Consistent rounding was one of the biggest audit findings. Early versions mixed `16px`, `20px`, `24px` arbitrarily. I consolidated to a named scale so everything feels intentional.

### Elevation

Cards use a two-layer shadow: a large soft ambient layer plus a tight colored key shadow that tints to Sunrise on hover. I deliberately avoided hard `box-shadow: 0 4px 6px black` patterns — the goal was depth without heaviness.

### Ghost Numbers

Large, low-opacity numbers (`opacity: 0.045`) sit behind section titles as dimensional background elements. They appear on step cards (`01`, `02`, `03`) and page headers (step number extracted from "3 / 5"). This technique costs nothing in layout but gives pages a sense of scale and intentionality.

---

## Animation & Motion

### Page Transitions

Streamlit re-renders the DOM on every navigation. I exploited this by injecting a `<div class="ww-page-curtain">` with the current page name embedded in an HTML comment. React sees a content change, replaces the DOM node, and the CSS animation re-fires.

```
ww-curtain: opacity 0.80 → 0 over 0.32s
```

I initially set this to `0.52s` — it felt slow. After the QA pass I cut it to `0.32s`, which feels snappy without being jarring.

### Staggered Content Entrance

All content uses `.ww-anim` (`ww-fade-up`): a combined `translateY` + `opacity` + `filter: blur` entrance. Children get delay classes (`.ww-anim-1` through `.ww-anim-5`) with tightened stagger intervals: `0.04 / 0.09 / 0.14 / 0.20 / 0.26s`.

The blur component (`1.5px`) was controversial — I considered removing it entirely since it's barely perceptible. I kept it because it just slightly softens the entrance and prevents that "text snapping in" abruptness.

### Skeleton Loading

Rather than a generic spinner, cards shimmer with a background-position sweep:

```
ww-shimmer: background-position 200% → -100% over 1.9s
```

The shimmer gradient uses a faint amber tint (`rgba(255,171,64,0.14)`) at the peak so it feels on-brand rather than generic grey.

### Empty States

I built a custom SVG compass that floats with a compound `translateY + rotate` animation (`ww-float: 4.2s`). The rotation peaks at `+5deg` then settles back through `-2deg` — a pendulum effect that feels deliberate, not random. Empty states that just say "nothing here" are a UX failure; the compass makes waiting feel intentional.

---

## Information Architecture

### Sidebar Navigation

The flow is linear but the nav always shows all 9 pages. This was an intentional tradeoff:

- **Pro**: Power users can jump to any step. Useful in a demo or QA context.
- **Con**: New users might navigate out of order and hit warning states ("Complete your profile first").

I mitigated the second issue by adding gated warnings at the top of each page when prerequisites aren't met, and by adding a visible `1/5 → 2/5 → 3/5...` step counter in each page header.

### Step Counter

Every page header carries a `step="N / 5"` badge. The step number is extracted and rendered as a large ghost number behind the title, so users always know where they are in the funnel without a separate progress bar component.

### CTA Buttons as Navigation

Every page used to end with an `st.info()` message like "Go to Review to confirm details." These were dead ends — users had to find the right item in the sidebar themselves. I replaced them all with explicit navigation buttons that set a `_nav_target` session state key and trigger a rerun. The sidebar radio widget reads this key before instantiation so the selection updates correctly.

### Cognitive Load Reduction

- No confirmation dialogs — actions (parse, match, generate activities) just run
- No multi-step forms — profile is a single short form, trip description is a free-text area
- Inline success messages appear in-context rather than redirecting to a toast/notification system
- Variant-specific UX (A/B/C) only affects the Review page — all other pages are identical across variants, reducing scope of variance

---

## Accessibility & Responsiveness

### What I Did

- **WCAG AA contrast**: Form labels were at `opacity: 0.40` (failing contrast ratio on Base). Raised to `0.58`.
- **Nav items**: Inactive nav labels were at `opacity: 0.40`. Raised to `0.52`.
- **Tab labels**: Raised from `0.42` to `0.55`.
- **Focus rings**: Added `:focus-visible` outlines to all button variants (primary, secondary, form-submit) using a Sunrise-tinted ring. Mouse users don't see it; keyboard users do.
- **Mobile padding**: Added a `@media (max-width: 768px)` rule setting `padding: 2rem 1.25rem 5rem` on the main container, so content doesn't bleed to the edges on small screens.

### What I'd Still Fix

- **Semantic HTML**: All custom cards are `<div>`-based. They should use `<article>`, `<section>`, and proper heading hierarchy. Streamlit's markdown rendering makes this tricky.
- **Screen reader labels**: The match cards have compatibility percentages but no `aria-label` explaining what the percentage means.
- **Motion reduction**: There's no `prefers-reduced-motion` media query. The `ww-fade-up`, `ww-shimmer`, and `ww-float` animations would all need `@media (prefers-reduced-motion: reduce)` overrides.
- **Color-only signaling**: The confidence badge on the Review page uses color (red = high confidence, grey = low) without a text label differentiating the two states.
- **Tap targets**: Several tag pills and "Save" buttons are small. On mobile, tap targets should be at least 44×44px.

---

## Tradeoffs & Decisions

### What I Cut

| Thing I Cut | Why |
|-------------|-----|
| Framer Motion for transitions | Streamlit blocks React-level JS injection. Pure CSS was the only path. |
| External icon library | Added weight with no payoff — Unicode symbols and simple SVG inline were sufficient. |
| Dark mode | Would require duplicating the entire token set. The warm palette doesn't invert cleanly. Punted. |
| Modal dialogs for confirmations | Streamlit doesn't support modals natively. Inline warnings are simpler and less disruptive. |
| Animated gradient background | Early prototype had it. It was visually loud and competed with card content. Replaced with static blobs. |
| `.ww-card::before` border-radius on accent stripe | The `0 0 3px 3px` value caused a slight visual artifact at the bottom corners of the stripe. Removed — `overflow: hidden` on the card handles clipping cleanly. |

### What I Kept (and Why)

- **Card hover tilt** (`rotate(-0.3deg)`): Tiny but tactile. Makes cards feel physical rather than flat.
- **Ghost numbers**: High visual payoff for zero extra layout cost.
- **Skeleton cards with shimmer**: Better than spinners because they set spatial expectations for what's loading.
- **Balloons on key actions**: Deliberately kept as a lightweight celebration moment. Matches Streamlit's personality.

### Key Risks

- **Streamlit CSS fragility**: All styling hooks into Streamlit's internal DOM structure (e.g., `[data-testid="stSidebar"]`). These selectors can break on Streamlit version updates.
- **Hardcoded breakpoint**: The `768px` breakpoint is a guess — no real device testing done.
- **Animation performance on low-end devices**: The page curtain, card shimmer, and float animation all run simultaneously. On CPU-only rendering this might be choppy.

---

## Before / After Highlights

- **Navigation dead ends**: Every "Go to X" message was a static `st.info()` call. After the audit, every end-of-step action renders a real navigation button that programmatically updates the sidebar selection.
- **Home page**: Was an empty `if page == "Home": st.write("Welcome")` placeholder. Became a full hero section with animated headline, gradient text accent, stat strip, and step cards with ghost numbers.
- **Empty states**: "No matches yet" was a plain `render_warning_message()` call — orange warning box, no context. Replaced with an animated SVG compass and a descriptive body line.
- **Card hover**: No hover states at all initially. Added a multi-layer shadow lift (`translateY(-5px)`), a Sunrise accent stripe that scales in on hover, and a slight tilt — all CSS, no JS.
- **Form label contrast**: Labels were `opacity: 0.40` — visually quiet but failing WCAG AA. Raised to `0.58` across all inputs, selects, and sliders.
- **Sidebar gap**: Nav items were `gap: 0.1rem`, so the glow halo of the active pill bled into adjacent items. Increased to `0.3rem` to give each item visual breathing room.

---

## What I'd Do Next

### Product Iteration

- **Onboarding flow**: The current profile form asks for name, age, and verification level — that's not enough signal for good matching. I'd add travel style preferences (solo vs. group tendency, introvert/extrovert, morning vs. night person) as a second step.
- **Match messaging**: Right now "Activities with {name}" generates a list but there's no in-app messaging. The next step is a lightweight async message thread per match.
- **Saved trips**: Users can only have one active trip at a time. A trip history/drafts panel would let returning users pick up where they left off.

### Design Iteration

- **Responsive layout pass**: Test on actual mobile devices, fix tap target sizes, add a collapsible sidebar for narrow viewports.
- **Add `prefers-reduced-motion`**: Wrap all keyframe animations in a `@media (prefers-reduced-motion: no-preference)` guard.
- **Typography refinement**: The Syne display font is expressive but heavy at large sizes on mobile. Consider a fluid type scale with `clamp()` for the hero headline.

### Experiments & Success Metrics

**Experiment 1 — CTA copy on Review page**
- Variant A: "Looks good — find matches" (current)
- Variant B: "Find my people →"
- Metric: click-through rate on the primary CTA; target >75%

**Experiment 2 — Match card density**
- Variant A: Full card with explanation text, activity tags, trust score (current)
- Variant B: Compact card — name, score, top 2 shared activities only
- Metric: time-to-first-match-click; target reduction of >20% for Variant B

**Experiment 3 — Empty state treatment on Matches**
- Variant A: Animated compass with copy (current)
- Variant B: "You're 2 steps away" mini progress indicator with direct CTAs to Profile and Trip
- Metric: funnel continuation rate from Matches empty state; target >40%

---

*All CSS lives in `src/wanderwing/frontend/utils/styling.py`. All page logic lives in `src/wanderwing/frontend/views/`. The design system tokens (colors, radii, type) are defined as CSS custom properties within the `apply_custom_css()` function.*
