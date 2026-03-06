"""WanderWing — Gradient Drift design system.

─────────────────────────────────────────────
TOKEN REFERENCE
─────────────────────────────────────────────
COLORS
  --sunrise   #FF6B6B   coral-red   primary accent
  --amber     #FFAB40   warm orange secondary accent
  --sky       #6EC6FF   soft blue   tertiary accent
  --base      #FFFBF5   warm white  page background
  --ink       #1A1A2E   navy-black  primary text

GRADIENTS
  --grad-primary  135deg  sunrise → amber     (buttons, highlights)
  --grad-sky      135deg  amber   → sky       (secondary moments)
  --grad-hero     135deg  sunrise → amber → sky  (hero display)
  --grad-blob-a   radial  sunrise 15%         (bg shape A)
  --grad-blob-b   radial  amber   12%         (bg shape B)
  --grad-blob-c   radial  sky      8%         (bg shape C)

RADIUS
  --r-xs   8px     tags, badges
  --r-sm   14px    inputs, small panels
  --r-md   24px    cards
  --r-lg   32px    modal, hero panels
  --r-pill 100px   buttons, pills

SHADOWS
  --shadow-card        sunrise-tinted resting shadow
  --shadow-card-hover  lifted card state
  --shadow-btn         gradient button glow
  --shadow-btn-hover   intensified button glow

SPACING   4 · 8 · 12 · 20 · 32 · 48 · 80px

BLUR      sm 8px · md 20px · lg 40px

─────────────────────────────────────────────
TYPE SCALE
─────────────────────────────────────────────
Display   Syne  800  4.5rem   -0.03em  hero only
H1        Syne  700  3rem     -0.02em
H2        Syne  700  1.85rem  -0.01em
H3        Inter 600  1.1rem   0
Body      Inter 400  1rem     1.65lh
Body SM   Inter 400  0.9rem   1.6lh
Label     Inter 600  0.72rem  0.09em  UPPERCASE
Caption   Inter 400  0.8rem   ink/55%
Number    Syne  700  large metrics

─────────────────────────────────────────────
MOTION
─────────────────────────────────────────────
fade-up:     translateY(24px)→0, 0.6s, spring
blob-drift:  translate+scale, 20-28s, ease-in-out
card-hover:  translateY(-6px), 0.25s, spring
btn-hover:   translateY(-3px) + glow, 0.18s, spring
btn-press:   translateY(1px), 0.08s, ease-out
stagger:     0.06s per .ww-anim-N (N=1–5)
easing:      cubic-bezier(0.22, 1, 0.36, 1)  — spring
             cubic-bezier(0.34, 1.56, 0.64, 1) — bouncy spring
"""

import streamlit as st


# ── Color tokens (Python constants for use in f-strings) ──────────────────────
C_SUNRISE = "#FF6B6B"
C_AMBER   = "#FFAB40"
C_SKY     = "#6EC6FF"
C_BASE    = "#FFFBF5"
C_INK     = "#1A1A2E"

GRAD_PRIMARY = "linear-gradient(135deg, #FF6B6B 0%, #FFAB40 100%)"
GRAD_SKY     = "linear-gradient(135deg, #FFAB40 0%, #6EC6FF 100%)"
GRAD_HERO    = "linear-gradient(135deg, #FF6B6B 0%, #FFAB40 50%, #6EC6FF 100%)"


def apply_custom_css() -> None:
    st.markdown(
        """<style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        /* ─── MULTIPAGE NAV ─────────────────────────── */
        [data-testid="stSidebarNav"] { display: none !important; }

        /* ─── CSS CUSTOM PROPERTIES ─────────────────── */
        :root {
            --sunrise: #FF6B6B;
            --amber:   #FFAB40;
            --sky:     #6EC6FF;
            --base:    #FFFBF5;
            --ink:     #1A1A2E;

            --grad-primary: linear-gradient(135deg, #FF6B6B 0%, #FFAB40 100%);
            --grad-sky:     linear-gradient(135deg, #FFAB40 0%, #6EC6FF 100%);
            --grad-hero:    linear-gradient(135deg, #FF6B6B 0%, #FFAB40 50%, #6EC6FF 100%);

            --r-xs:   8px;
            --r-sm:   14px;
            --r-md:   24px;
            --r-lg:   32px;
            --r-pill: 100px;

            --shadow-card:       0 4px 24px rgba(255,107,107,0.10), 0 1px 4px rgba(26,26,46,0.06);
            --shadow-card-hover: 0 20px 56px rgba(255,107,107,0.16), 0 4px 16px rgba(26,26,46,0.08);
            --shadow-btn:        0 4px 20px rgba(255,107,107,0.38);
            --shadow-btn-hover:  0 10px 36px rgba(255,107,107,0.50);

            --ease-spring: cubic-bezier(0.22, 1, 0.36, 1);
            --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        /* ─── RESET ──────────────────────────────────── */
        *, *::before, *::after { box-sizing: border-box; }

        /* ─── BASE FONTS ─────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* ─── PAGE BACKGROUND + CORNER GRADIENT WASHES ─ */
        .stApp {
            background-color: #FFFBF5 !important;
            /* Four corner washes: top-right sunrise, bottom-left amber,
               top-left sky, bottom-right soft sunrise */
            background-image:
                radial-gradient(ellipse 80% 55% at 108% -3%,  rgba(255,107,107,0.10) 0%, transparent 65%),
                radial-gradient(ellipse 72% 52% at -8%  108%, rgba(255,171,64,0.09)  0%, transparent 65%),
                radial-gradient(ellipse 60% 48% at -5%  -5%,  rgba(110,198,255,0.08) 0%, transparent 62%),
                radial-gradient(ellipse 55% 45% at 108% 108%, rgba(255,107,107,0.05) 0%, transparent 62%) !important;
            background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100% !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed, fixed, fixed, fixed !important;
        }
        /* iOS Safari: fixed attachment causes repaints, use scroll fallback */
        @supports (-webkit-touch-callout: none) {
            .stApp { background-attachment: scroll, scroll, scroll, scroll !important; }
        }

        /* ─── BACKGROUND BLOBS ───────────────────────── */
        /* Blob A — sunrise, large, top-right, organic shape */
        .stApp::before {
            content: '';
            position: fixed;
            top: -20%;
            right: -16%;
            width: clamp(360px, 55vw, 780px);
            height: clamp(360px, 55vw, 780px);
            background: radial-gradient(ellipse at 40% 45%,
                rgba(255,107,107,0.17) 0%,
                rgba(255,171,64,0.08)  42%,
                transparent 68%);
            border-radius: 62% 38% 58% 42% / 42% 62% 38% 58%;
            z-index: 0;
            pointer-events: none;
            animation: ww-blob-a 22s ease-in-out infinite;
            will-change: transform;
        }
        /* Blob B — amber, large, bottom-left, organic shape */
        .stApp::after {
            content: '';
            position: fixed;
            bottom: -18%;
            left: -12%;
            width: clamp(300px, 48vw, 700px);
            height: clamp(300px, 48vw, 700px);
            background: radial-gradient(ellipse at 55% 50%,
                rgba(255,171,64,0.16) 0%,
                rgba(255,107,107,0.05) 42%,
                transparent 68%);
            border-radius: 45% 55% 62% 38% / 55% 42% 58% 45%;
            z-index: 0;
            pointer-events: none;
            animation: ww-blob-b 28s ease-in-out infinite;
            will-change: transform;
        }
        /* Blob C — sky, mid-right */
        section.main::before {
            content: '';
            position: fixed;
            top: 22%;
            right: -10%;
            width: clamp(200px, 30vw, 480px);
            height: clamp(200px, 30vw, 480px);
            background: radial-gradient(ellipse at center,
                rgba(110,198,255,0.14) 0%,
                rgba(110,198,255,0.04) 45%,
                transparent 68%);
            border-radius: 52% 48% 44% 56% / 60% 38% 62% 40%;
            z-index: 0;
            pointer-events: none;
            animation: ww-blob-c 19s ease-in-out infinite;
            will-change: transform;
        }
        /* Blob D — sunrise small, upper-center (drifts in reverse) */
        section.main::after {
            content: '';
            position: fixed;
            top: 12%;
            left: 22%;
            width: clamp(150px, 20vw, 340px);
            height: clamp(150px, 20vw, 340px);
            background: radial-gradient(ellipse at center,
                rgba(255,107,107,0.09) 0%,
                rgba(255,171,64,0.04)  40%,
                transparent 68%);
            border-radius: 70% 30% 52% 48% / 38% 62% 38% 62%;
            z-index: 0;
            pointer-events: none;
            animation: ww-blob-d 25s ease-in-out infinite reverse;
            will-change: transform;
        }
        /* Blob E — sky accent, sidebar mid */
        [data-testid="stSidebar"]::after {
            content: '';
            position: fixed;
            top: 38%;
            left: 3%;
            width: clamp(180px, 22vw, 360px);
            height: clamp(180px, 22vw, 360px);
            background: radial-gradient(ellipse at center,
                rgba(110,198,255,0.11) 0%,
                transparent 68%);
            border-radius: 55% 45% 48% 52% / 62% 38% 58% 42%;
            z-index: 0;
            pointer-events: none;
            animation: ww-blob-c 18s ease-in-out infinite 4s;
            will-change: transform;
        }
        /* Noise texture overlay — very subtle grain */
        [data-testid="stMainBlockContainer"]::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.80' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
            background-size: 200px 200px;
            background-repeat: repeat;
            opacity: 0.022;
            z-index: 0;
            pointer-events: none;
        }

        /* ─── READABILITY: content above all blobs ────── */
        [data-testid="stMainBlockContainer"],
        [data-testid="stSidebar"] > div {
            position: relative;
            z-index: 1;
        }
        /* Extra isolation so cards/inputs always sit above blobs */
        .ww-card, .stButton, .stTextInput, .stTextArea,
        .stSelectbox, .stSlider, .stForm, .stTabs,
        [data-testid="stExpander"] {
            position: relative;
            z-index: 2;
        }

        /* ─── MOBILE: scale back blobs + disable fixed bg ─ */
        @media (max-width: 768px) {
            .stApp::before  { opacity: 0.75; }
            .stApp::after   { opacity: 0.75; }
            section.main::before { opacity: 0.65; }
            section.main::after  { opacity: 0.55; }
            [data-testid="stSidebar"]::after { display: none; }
            [data-testid="stMainBlockContainer"]::before { opacity: 0.015; }
            .stApp { background-attachment: scroll, scroll, scroll, scroll !important; }
        }

        /* ─── LAYOUT ─────────────────────────────────── */
        section.main { position: relative; }
        .main .block-container {
            padding: 4rem 4rem 8rem;
            max-width: 840px;
            margin: 0 auto;
        }

        /* ─── TYPOGRAPHY ─────────────────────────────── */
        h1 {
            font-family: 'Syne', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            line-height: 1.08;
            letter-spacing: -0.025em;
            color: #1A1A2E;
            margin-bottom: 0.5rem;
        }
        h2 {
            font-family: 'Syne', sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.015em;
            color: #1A1A2E;
            margin-bottom: 0.4rem;
        }
        h3 {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: #1A1A2E;
            margin-bottom: 0.4rem;
        }
        p {
            font-size: 1rem;
            line-height: 1.7;
            color: rgba(26,26,46,0.58);
        }
        strong, b { color: #1A1A2E; font-weight: 600; }
        hr {
            border: none;
            border-top: 1px solid rgba(26,26,46,0.08);
            margin: 2.5rem 0;
        }

        /* ─── SIDEBAR ────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: rgba(255,251,245,0.94) !important;
            border-right: 1px solid rgba(255,107,107,0.10) !important;
            backdrop-filter: blur(16px);
        }
        [data-testid="stSidebar"] > div { padding: 2rem 1.25rem; }

        /* ─── NAV — pill style ────────────────────────── */
        [data-testid="stSidebar"] .stRadio > div {
            flex-direction: column !important;
            gap: 0.3rem !important;
        }
        /* Hide the radio dot */
        [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        /* Base nav item */
        [data-testid="stSidebar"] .stRadio label {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            color: rgba(26,26,46,0.52) !important;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            padding: 0.52rem 0.9rem !important;
            margin: 0 -0.1rem !important;
            border-radius: 100px !important;
            cursor: pointer;
            display: block !important;
            transition: background 0.20s cubic-bezier(0.22,1,0.36,1),
                        color 0.16s ease,
                        box-shadow 0.20s ease !important;
        }
        /* Hover: warm tint pill */
        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255,107,107,0.07) !important;
            color: rgba(26,26,46,0.72) !important;
        }
        /* Active: filled gradient pill */
        [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:has(input:checked) label {
            background: linear-gradient(135deg, #FF6B6B 0%, #FFAB40 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 16px rgba(255,107,107,0.32),
                        0 1px 4px rgba(255,107,107,0.18) !important;
            letter-spacing: 0.08em !important;
        }

        /* ─── BUTTONS ────────────────────────────────── */
        .stButton > button {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            border-radius: 100px;
            padding: 0.8rem 2.25rem;
            border: none;
            cursor: pointer;
            transform-origin: center center;
            transition: transform 0.22s cubic-bezier(0.22,1,0.36,1),
                        box-shadow 0.22s cubic-bezier(0.22,1,0.36,1),
                        background-position 0.55s ease;
        }
        /* ── Primary: gradient fill + subtle position sweep ─ */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg,
                #FF6B6B 0%, #FFAB40 55%, #FF6B6B 100%) !important;
            background-size: 220% 100% !important;
            background-position: 0% center !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 20px rgba(255,107,107,0.34) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-position: 100% center !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 32px rgba(255,107,107,0.42) !important;
        }
        .stButton > button[kind="primary"]:focus-visible {
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(255,107,107,0.38) !important;
        }
        /* Squish on press: fast compress, spring release */
        .stButton > button[kind="primary"]:active {
            transform: scaleX(0.96) scaleY(0.90) translateY(1px) !important;
            box-shadow: 0 2px 10px rgba(255,107,107,0.25) !important;
            transition: transform 0.07s ease-out, box-shadow 0.07s ease-out !important;
        }
        /* ── Secondary: outlined + warm fill on hover ── */
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind="primary"]) {
            background: rgba(255,255,255,0.88) !important;
            color: #1A1A2E !important;
            border: 1.5px solid rgba(26,26,46,0.14) !important;
            box-shadow: 0 2px 8px rgba(26,26,46,0.05) !important;
        }
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind="primary"]):hover {
            background: #FFFFFF !important;
            border-color: rgba(255,107,107,0.40) !important;
            color: #FF6B6B !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 24px rgba(255,107,107,0.14),
                        0 2px 6px rgba(255,107,107,0.08) !important;
        }
        .stButton > button[kind="secondary"]:active,
        .stButton > button:not([kind="primary"]):active {
            transform: scaleX(0.97) scaleY(0.93) !important;
            transition: transform 0.07s ease-out !important;
        }
        .stButton > button[kind="secondary"]:focus-visible,
        .stButton > button:not([kind="primary"]):focus-visible {
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(255,107,107,0.28) !important;
        }
        /* ── Form submit (stFormSubmitButton) ────────── */
        [data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #FF6B6B 0%, #FFAB40 55%, #FF6B6B 100%) !important;
            background-size: 220% 100% !important;
            background-position: 0% center !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 100px !important;
            box-shadow: 0 4px 22px rgba(255,107,107,0.38) !important;
            transition: transform 0.22s cubic-bezier(0.22,1,0.36,1),
                        box-shadow 0.22s cubic-bezier(0.22,1,0.36,1),
                        background-position 0.55s ease !important;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            background-position: 100% center !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 32px rgba(255,107,107,0.42) !important;
        }
        [data-testid="stFormSubmitButton"] > button:active {
            transform: scaleX(0.96) scaleY(0.90) translateY(1px) !important;
            transition: transform 0.07s ease-out !important;
        }
        [data-testid="stFormSubmitButton"] > button:focus-visible {
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(255,107,107,0.38) !important;
        }

        /* ─── INPUTS ─────────────────────────────────── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            line-height: 1.6;
            border-radius: 14px;
            border: 2px solid rgba(26,26,46,0.10) !important;
            background: rgba(255,255,255,0.92) !important;
            color: #1A1A2E;
            padding: 0.82rem 1.1rem;
            transition: border-color 0.2s ease, background 0.2s ease;
        }
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: rgba(26,26,46,0.28) !important;
        }
        .stTextInput > div > div > input:hover,
        .stTextArea > div > div > textarea:hover {
            border-color: rgba(255,107,107,0.30) !important;
            background: rgba(255,255,255,0.97) !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #FF6B6B !important;
            background: #FFFFFF !important;
            outline: none !important;
            animation: ww-focus-ring 0.55s cubic-bezier(0.22,1,0.36,1) forwards;
        }
        /* Field labels — WCAG AA: min 4.5:1 ratio */
        .stTextInput label, .stTextArea label,
        .stSelectbox label, .stSlider label,
        .stRadio > label {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            color: rgba(26,26,46,0.58) !important;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            margin-bottom: 0.45rem;
        }
        /* Select */
        .stSelectbox > div > div {
            border-radius: 14px !important;
            border: 2px solid rgba(26,26,46,0.10) !important;
            background: rgba(255,255,255,0.92) !important;
            font-family: 'Inter', sans-serif;
            transition: border-color 0.2s ease;
        }
        .stSelectbox > div > div:hover {
            border-color: rgba(255,107,107,0.30) !important;
        }
        /* Slider track */
        .stSlider > div > div > div > div { background: #FF6B6B !important; }
        /* Slider thumb — bouncy scale on hover */
        [data-testid="stSlider"] [role="slider"] {
            background: linear-gradient(135deg, #FF6B6B, #FFAB40) !important;
            border: none !important;
            width: 18px !important;
            height: 18px !important;
            box-shadow: 0 2px 10px rgba(255,107,107,0.42) !important;
            transition: transform 0.18s cubic-bezier(0.34,1.56,0.64,1) !important;
        }
        [data-testid="stSlider"] [role="slider"]:hover {
            transform: scale(1.22) !important;
        }
        [data-testid="stSlider"] [role="slider"]:active {
            transform: scale(1.15) !important;
        }

        /* ─── FORM ───────────────────────────────────── */
        .stForm { background: transparent !important; border: none !important; }

        /* ─── TABS — pill capsule style ──────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(26,26,46,0.05) !important;
            border-radius: 100px !important;
            padding: 4px 4px !important;
            border-bottom: none !important;
            gap: 2px !important;
            width: fit-content !important;
            margin-bottom: 1.5rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.70rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: rgba(26,26,46,0.55) !important;
            padding: 0.50rem 1.1rem !important;
            border-radius: 100px !important;
            background: transparent !important;
            border: none !important;
            transition: background 0.20s cubic-bezier(0.22,1,0.36,1),
                        color 0.16s ease,
                        box-shadow 0.20s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255,255,255,0.70) !important;
            color: rgba(26,26,46,0.72) !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #FF6B6B 0%, #FFAB40 100%) !important;
            color: #FFFFFF !important;
            border-bottom: none !important;
            box-shadow: 0 3px 14px rgba(255,107,107,0.32) !important;
        }
        .stTabs [data-baseweb="tab-panel"] { padding-top: 0 !important; }

        /* ─── EXPANDER ───────────────────────────────── */
        [data-testid="stExpander"] {
            border: 1.5px solid rgba(255,107,107,0.10) !important;
            border-radius: 18px !important;
            background: rgba(255,255,255,0.88) !important;
            margin-bottom: 0.75rem;
            transition: border-color 0.20s ease, box-shadow 0.20s ease;
        }
        [data-testid="stExpander"]:hover {
            border-color: rgba(255,107,107,0.22) !important;
            box-shadow: 0 4px 16px rgba(255,107,107,0.08) !important;
        }
        [data-testid="stExpander"] summary {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: rgba(26,26,46,0.55) !important;
            padding: 1rem 1.25rem;
        }

        /* ─── DATAFRAME ──────────────────────────────── */
        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,107,107,0.10);
        }
        [data-testid="stDataFrame"] table { font-family: 'Inter', sans-serif; font-size: 0.88rem; }

        /* ─── PROGRESS ───────────────────────────────── */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #FF6B6B, #FFAB40);
            border-radius: 4px;
        }

        /* ─── SPINNER — brand-styled loading ring ────── */
        [data-testid="stSpinner"] > div > div {
            width: 22px !important; height: 22px !important;
            border-width: 2.5px !important;
            border-color: rgba(255,107,107,0.15) !important;
            border-top-color: #FF6B6B !important;
        }
        [data-testid="stSpinner"] p {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.88rem !important;
            color: rgba(26,26,46,0.45) !important;
            font-weight: 500 !important;
        }

        /* ─── ALERTS — rounded + brand tones ────────── */
        [data-testid="stAlert"] {
            border-radius: 16px !important;
            border: none !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
        }
        /* success alert — sky tint */
        [data-testid="stAlert"][kind="success"],
        div[data-baseweb="notification"][kind="positive"] {
            background: rgba(110,198,255,0.12) !important;
        }
        /* error / warning */
        [data-testid="stAlert"][kind="error"],
        div[data-baseweb="notification"][kind="negative"] {
            background: rgba(255,107,107,0.10) !important;
        }

        /* ─── METRICS — accent delta color ──────────── */
        [data-testid="stMetricValue"] {
            font-family: 'Syne', sans-serif !important;
            font-size: 2.6rem !important;
            font-weight: 800 !important;
            color: #1A1A2E !important;
            letter-spacing: -0.025em;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            color: rgba(26,26,46,0.40) !important;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.82rem !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricDelta"] svg { display: none !important; }
        [data-testid="stMetricDelta"][data-direction="up"] {
            color: #FF6B6B !important;
        }

        /* ─── ANIMATIONS ─────────────────────────────── */
        @keyframes ww-fade-up {
            from { opacity: 0; transform: translateY(16px); filter: blur(1.5px); }
            to   { opacity: 1; transform: translateY(0);    filter: blur(0);     }
        }
        /* Focus ring pulse — expands then settles */
        @keyframes ww-focus-ring {
            0%   { box-shadow: 0 0 0 0   rgba(255,107,107,0.45); }
            55%  { box-shadow: 0 0 0 6px rgba(255,107,107,0.12); }
            100% { box-shadow: 0 0 0 4px rgba(255,107,107,0.10); }
        }
        /* Spinner pulse — subtle opacity throb on the ring */
        @keyframes ww-spin {
            from { transform: rotate(0deg); }
            to   { transform: rotate(360deg); }
        }
        @keyframes ww-blob-a {
            0%,100% { transform: translate(0,0) scale(1); }
            33%     { transform: translate(40px,-35px) scale(1.06); }
            66%     { transform: translate(-25px,20px) scale(0.96); }
        }
        @keyframes ww-blob-b {
            0%,100% { transform: translate(0,0) scale(1); }
            33%     { transform: translate(-30px,40px) scale(1.04); }
            66%     { transform: translate(25px,-20px) scale(0.97); }
        }
        @keyframes ww-blob-c {
            0%,100% { transform: translate(0,0) scale(1); }
            40%     { transform: translate(18px,-22px) scale(1.06); }
            75%     { transform: translate(-12px,15px) scale(0.96); }
        }
        @keyframes ww-blob-d {
            0%,100% { transform: translate(0,0) scale(1) rotate(0deg); }
            30%     { transform: translate(25px,18px) scale(1.08) rotate(6deg); }
            65%     { transform: translate(-18px,-14px) scale(0.93) rotate(-4deg); }
        }

        /* ─── ANIMATION CLASSES ──────────────────────── */
        .ww-anim   { animation: ww-fade-up 0.52s cubic-bezier(0.22,1,0.36,1) both; }
        .ww-anim-1 { animation-delay: 0.04s; }
        .ww-anim-2 { animation-delay: 0.09s; }
        .ww-anim-3 { animation-delay: 0.14s; }
        .ww-anim-4 { animation-delay: 0.20s; }
        .ww-anim-5 { animation-delay: 0.26s; }

        /* ─── CARD COMPONENT ─────────────────────────── */
        .ww-card {
            background: rgba(255,255,255,0.90);
            border-radius: 24px;
            padding: 2rem 2.25rem;
            border: 1px solid rgba(255,107,107,0.10);
            box-shadow: 0 4px 24px rgba(255,107,107,0.10), 0 1px 4px rgba(26,26,46,0.06);
            transition: transform 0.30s cubic-bezier(0.22,1,0.36,1),
                        box-shadow 0.30s cubic-bezier(0.22,1,0.36,1),
                        border-color 0.25s ease;
            margin-bottom: 1.25rem;
            /* Needed for the top accent stripe */
            position: relative;
            overflow: hidden;
            transform-origin: center 80%;
        }
        /* Top accent stripe — slides in on hover */
        .ww-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #FF6B6B 0%, #FFAB40 50%, #6EC6FF 100%);
            transform: scaleX(0);
            transform-origin: left center;
            transition: transform 0.35s cubic-bezier(0.22,1,0.36,1);
        }
        .ww-card:hover::before { transform: scaleX(1); }
        /* Lift — subtle tilt, two-layer shadow */
        .ww-card:hover {
            transform: translateY(-5px) rotate(-0.3deg);
            box-shadow: 0 14px 40px rgba(255,107,107,0.13), 0 4px 12px rgba(26,26,46,0.07);
            border-color: rgba(255,107,107,0.20);
        }

        /* ─── STEP INDICATOR ─────────────────────────── */
        .ww-step {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: rgba(26,26,46,0.35);
            margin-bottom: 1rem;
        }

        /* ─── EYEBROW ────────────────────────────────── */
        .ww-eyebrow {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            background: linear-gradient(135deg, #FF6B6B, #FFAB40);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.75rem;
        }

        /* ─── PILL ───────────────────────────────────── */
        .ww-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.28rem 0.85rem;
            border-radius: 100px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }
        .ww-pill-sunrise { background: rgba(255,107,107,0.10); color: #FF6B6B; }
        .ww-pill-amber   { background: rgba(255,171,64,0.12);  color: #E8960A; }
        .ww-pill-sky     { background: rgba(110,198,255,0.14); color: #2B8CC4; }
        .ww-pill-ink     { background: rgba(26,26,46,0.07);    color: rgba(26,26,46,0.70); }
        /* legacy alias */
        .ww-pill-fire    { background: rgba(255,107,107,0.10); color: #FF6B6B; }

        /* ─── RULE ───────────────────────────────────── */
        .ww-rule { height: 1px; background: rgba(26,26,46,0.07); margin: 1.5rem 0; }

        /* ─── GRADIENT TEXT UTILITY ──────────────────── */
        .ww-grad-text {
            background: linear-gradient(135deg, #FF6B6B, #FFAB40);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* ═══════════════════════════════════════════════
           PERSONALITY & LAYOUT COMPONENTS
        ═══════════════════════════════════════════════ */

        /* ─── DISPLAY HEADLINE ───────────────────────── */
        .ww-display {
            font-family: 'Syne', sans-serif;
            font-size: clamp(2.8rem, 6.5vw, 5rem);
            font-weight: 800;
            line-height: 1.02;
            letter-spacing: -0.03em;
            color: #1A1A2E;
            margin: 0.4rem 0 1.2rem;
            position: relative;
            z-index: 1;
        }

        /* ─── HERO SECTION ───────────────────────────── */
        .ww-hero {
            position: relative;
            padding: 3rem 0 3.5rem;
            overflow: visible;
        }
        /* Decorative shape behind hero — supplement background blobs */
        .ww-hero::after {
            content: '';
            position: absolute;
            top: -40%;
            right: -5%;
            width: clamp(240px, 38vw, 520px);
            height: clamp(240px, 38vw, 520px);
            background: radial-gradient(ellipse at 42% 44%,
                rgba(255,171,64,0.16) 0%,
                rgba(255,107,107,0.07) 45%,
                transparent 70%);
            border-radius: 60% 40% 52% 48% / 44% 56% 44% 56%;
            pointer-events: none;
            z-index: 0;
            animation: ww-blob-b 26s ease-in-out infinite 5s;
            will-change: transform;
        }

        /* ─── HERO TAG (pill above headline) ─────────── */
        .ww-hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: rgba(255,107,107,0.10);
            color: #FF6B6B;
            border-radius: 100px;
            padding: 0.38rem 1rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.70rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 1.25rem;
            position: relative;
            z-index: 1;
        }
        .ww-hero-tag::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #FF6B6B;
            box-shadow: 0 0 0 0 rgba(255,107,107,0.5);
            animation: ww-ping 2s ease-in-out infinite;
        }
        @keyframes ww-ping {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255,107,107,0.5); }
            50%       { box-shadow: 0 0 0 5px rgba(255,107,107,0); }
        }

        /* ─── STAT BLOCK ─────────────────────────────── */
        .ww-stat { display: flex; flex-direction: column; gap: 0.2rem; }
        .ww-stat-val {
            font-family: 'Syne', sans-serif;
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1;
            background: linear-gradient(135deg, #FF6B6B 0%, #FFAB40 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .ww-stat-label {
            font-size: 0.70rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.11em;
            color: rgba(26,26,46,0.35);
        }

        /* ─── STEP CARD (how it works) ───────────────── */
        .ww-step-card {
            position: relative;
            padding: 1.75rem 1.5rem 2rem;
            background: rgba(255,255,255,0.82);
            border-radius: 22px;
            border: 1px solid rgba(255,107,107,0.09);
            height: 100%;
            transition: transform 0.28s cubic-bezier(0.22,1,0.36,1),
                        box-shadow 0.28s ease;
        }
        .ww-step-card:hover {
            transform: translateY(-5px) rotate(-0.3deg);
            box-shadow: 0 14px 40px rgba(255,107,107,0.12), 0 4px 10px rgba(26,26,46,0.06);
        }
        /* Ghost step number — absolutely positioned in corner */
        .ww-step-ghost {
            position: absolute;
            bottom: -0.15em;
            right: 0.05em;
            font-family: 'Syne', sans-serif;
            font-size: clamp(4rem, 8vw, 6rem);
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.05em;
            color: rgba(255,107,107,0.07);
            pointer-events: none;
            user-select: none;
            z-index: 0;
        }
        .ww-step-card > *:not(.ww-step-ghost) { position: relative; z-index: 1; }

        /* Middle step pushed down for asymmetry */
        .ww-step-mid { margin-top: 2.5rem; }

        /* ─── SECTION HEADER (big + editorial) ──────── */
        .ww-section-head {
            position: relative;
            margin: 2.5rem 0 1.25rem;
            padding-top: 0.25rem;
        }
        /* Ghost oversize number behind section title */
        .ww-overnum {
            position: absolute;
            top: -0.35em;
            left: -0.12em;
            font-family: 'Syne', sans-serif;
            font-size: 8rem;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.05em;
            color: rgba(255,107,107,0.065);
            pointer-events: none;
            user-select: none;
            z-index: 0;
        }
        .ww-section-eyebrow {
            display: block;
            font-family: 'Inter', sans-serif;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: #FF6B6B;
            margin-bottom: 0.3rem;
            position: relative;
            z-index: 1;
        }
        .ww-section-title {
            font-family: 'Syne', sans-serif;
            font-size: clamp(1.5rem, 3vw, 2rem);
            font-weight: 800;
            color: #1A1A2E;
            letter-spacing: -0.025em;
            line-height: 1.1;
            position: relative;
            z-index: 1;
            margin: 0;
        }

        /* ─── FEATURE HIGHLIGHT BLOCK ────────────────── */
        .ww-feature {
            position: relative;
            padding: 2.25rem 2.5rem 2.25rem 2.75rem;
            border-radius: 28px;
            overflow: hidden;
            background: linear-gradient(140deg,
                rgba(255,107,107,0.07) 0%,
                rgba(255,171,64,0.04) 55%,
                rgba(110,198,255,0.04) 100%);
            border: 1px solid rgba(255,107,107,0.13);
            margin: 1.5rem 0;
        }
        /* Large organic blob behind feature content */
        .ww-feature::before {
            content: '';
            position: absolute;
            top: -35%;
            right: -18%;
            width: 70%;
            height: 170%;
            background: radial-gradient(ellipse at 50% 45%,
                rgba(255,171,64,0.12) 0%,
                rgba(255,107,107,0.04) 48%,
                transparent 70%);
            border-radius: 46% 54% 40% 60% / 56% 44% 60% 40%;
            pointer-events: none;
            z-index: 0;
        }
        /* Second smaller blob — bottom left */
        .ww-feature::after {
            content: '';
            position: absolute;
            bottom: -20%;
            left: -8%;
            width: 35%;
            height: 100%;
            background: radial-gradient(ellipse at center,
                rgba(110,198,255,0.08) 0%,
                transparent 68%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 0;
        }
        .ww-feature > * { position: relative; z-index: 1; }

        /* ─── OFFSET ACCENT PANEL ────────────────────── */
        .ww-offset-panel {
            margin-left: 1.75rem;
            padding-left: 1.25rem;
            border-left: 3px solid rgba(255,107,107,0.40);
        }

        /* ─── PAGE HEADER ghost number ───────────────── */
        .ww-page-ghost {
            position: absolute;
            top: -0.28em;
            left: -0.1em;
            font-family: 'Syne', sans-serif;
            font-size: 9rem;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.05em;
            color: rgba(255,107,107,0.065);
            pointer-events: none;
            user-select: none;
            z-index: 0;
        }

        /* ─── RESPONSIVE ────────────────────────────── */
        @media (max-width: 768px) {
            .main .block-container { padding: 2rem 1.25rem 5rem !important; }
            .ww-display { font-size: clamp(2.4rem, 10vw, 3.5rem); }
            .ww-step-mid { margin-top: 0; }
            .ww-feature { padding: 1.5rem 1.5rem 1.5rem 1.75rem; }
            .ww-overnum { font-size: 5rem; }
            .ww-page-ghost { font-size: 6rem; }
        }

        /* ════════════════════════════════════════════
           MOTION — PAGE TRANSITIONS, SKELETONS, EMPTY
           ════════════════════════════════════════════ */

        /* ─── PAGE TRANSITION CURTAIN ────────────────
           Injected via st.markdown with page name in HTML
           comment so React recreates the node on every
           navigation, triggering the fade-out animation. */
        .ww-page-curtain {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 450;
            background: #FFFBF5;
            animation: ww-curtain 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
        }
        @keyframes ww-curtain {
            0%   { opacity: 0.80; }
            100% { opacity: 0;    }
        }

        /* ─── SKELETON SHIMMER ───────────────────────
           Use .ww-skeleton on any div to get a soft
           shimmer sweep.  Combine with inline height/
           width to match the placeholder shape. */
        .ww-skeleton {
            position: relative;
            overflow: hidden;
            background: rgba(26,26,46,0.06);
            border-radius: 8px;
        }
        .ww-skeleton::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.72) 38%,
                rgba(255,171,64,0.14) 52%,
                transparent 100%
            );
            background-size: 300% 100%;
            animation: ww-shimmer 1.9s ease-in-out infinite;
        }
        @keyframes ww-shimmer {
            0%   { background-position: 200% center; }
            100% { background-position: -100% center; }
        }
        /* Skeleton text lines — composable shorthand */
        .ww-skel-line {
            display: block;
            height: 13px;
            border-radius: 5px;
            margin-bottom: 0.55rem;
        }
        .ww-skel-head {
            display: block;
            height: 10px;
            border-radius: 5px;
            width: 40%;
            margin-bottom: 1.1rem;
        }

        /* ─── EMPTY STATE ────────────────────────────*/
        .ww-empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 3.5rem 2rem 4rem;
        }
        .ww-empty-svg {
            animation: ww-float 4.2s ease-in-out infinite;
            margin-bottom: 1.75rem;
            opacity: 0.92;
        }
        @keyframes ww-float {
            0%,  100% { transform: translateY(0)     rotate(0deg);  }
            40%        { transform: translateY(-12px) rotate(5deg);  }
            70%        { transform: translateY(-6px)  rotate(-2deg); }
        }
        .ww-empty-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 800;
            color: #1A1A2E;
            letter-spacing: -0.02em;
            margin: 0 0 0.45rem;
        }
        .ww-empty-body {
            font-size: 0.875rem;
            color: rgba(26,26,46,0.45);
            line-height: 1.65;
            max-width: 240px;
            margin: 0 auto;
        }
        </style>""",
        unsafe_allow_html=True,
    )


# ── Token helpers (Python constants exposed for f-strings) ────────────────────

def _ink(opacity: float) -> str:
    """Return rgba ink color at given opacity."""
    return f"rgba(26,26,46,{opacity})"

def _sunrise(opacity: float) -> str:
    return f"rgba(255,107,107,{opacity})"

def _amber(opacity: float) -> str:
    return f"rgba(255,171,64,{opacity})"

def _sky(opacity: float) -> str:
    return f"rgba(110,198,255,{opacity})"


# ── Page-level helpers ────────────────────────────────────────────────────────


def render_page_header(title: str, subtitle: str = "", step: str | None = None) -> None:
    step_html = f'<div class="ww-step ww-anim">{step}</div>' if step else ""
    # Extract first digit from step for ghost number behind title (e.g. "2 / 5" → "2")
    ghost_num = step.split("/")[0].strip() if step else ""
    ghost_html = f'<span class="ww-page-ghost">{ghost_num}</span>' if ghost_num else ""
    sub_html = (
        f'<p class="ww-anim ww-anim-2" style="font-size:1.05rem;color:rgba(26,26,46,0.55);margin-top:0.5rem;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f'<div style="margin-bottom:2.5rem;position:relative;">'
        f'{ghost_html}{step_html}'
        f'<h1 class="ww-anim ww-anim-1" style="position:relative;z-index:1;">{title}</h1>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


def render_section_header(eyebrow: str, title: str, num: str | None = None) -> None:
    """Editorial section header with large ghost number and eyebrow label."""
    ghost_html = f'<span class="ww-overnum">{num}</span>' if num else ""
    st.markdown(
        f'<div class="ww-section-head">'
        f'{ghost_html}'
        f'<span class="ww-section-eyebrow">{eyebrow}</span>'
        f'<p class="ww-section-title">{title}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_feature_highlight(content_html: str) -> None:
    """Full-bleed feature block with organic gradient shapes behind content."""
    st.markdown(
        f'<div class="ww-feature">{content_html}</div>',
        unsafe_allow_html=True,
    )


# ── Motion helpers ─────────────────────────────────────────────────────────────

_COMPASS_SVG = (
    '<svg class="ww-empty-svg" width="110" height="110" viewBox="0 0 110 110" '
    'fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="55" cy="55" rx="50" ry="48" fill="rgba(255,107,107,0.08)"/>'
    '<circle cx="55" cy="55" r="28" stroke="rgba(255,107,107,0.22)" stroke-width="2" fill="none"/>'
    '<circle cx="55" cy="55" r="4" fill="rgba(255,107,107,0.40)"/>'
    '<path d="M55 55 L61 33 L55 40 Z" fill="#FF6B6B" opacity="0.75"/>'
    '<path d="M55 55 L49 33 L55 40 Z" fill="rgba(255,107,107,0.28)"/>'
    '<path d="M55 55 L61 77 L55 70 Z" fill="rgba(26,26,46,0.18)"/>'
    '<path d="M55 55 L49 77 L55 70 Z" fill="rgba(26,26,46,0.10)"/>'
    '<circle cx="55" cy="14" r="4.5" fill="rgba(255,171,64,0.55)"/>'
    '<circle cx="93" cy="55" r="3.5" fill="rgba(110,198,255,0.55)"/>'
    '<circle cx="17" cy="55" r="3.5" fill="rgba(255,107,107,0.35)"/>'
    '<circle cx="80" cy="20" r="2.5" fill="rgba(255,171,64,0.32)"/>'
    '<circle cx="30" cy="84" r="2" fill="rgba(110,198,255,0.28)"/>'
    '</svg>'
)


def render_empty_state(title: str, body: str = "") -> None:
    """Playful animated empty state with floating compass illustration."""
    body_html = f'<p class="ww-empty-body">{body}</p>' if body else ""
    st.markdown(
        f'<div class="ww-empty-state ww-anim">'
        f'{_COMPASS_SVG}'
        f'<p class="ww-empty-title">{title}</p>'
        f'{body_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_skeleton_card(lines: int = 3, has_header: bool = True) -> None:
    """Shimmer placeholder for a card that is loading."""
    header_html = (
        '<span class="ww-skeleton ww-skel-head"></span>' if has_header else ""
    )
    widths = [90, 74, 58, 44, 68]
    lines_html = "".join(
        f'<span class="ww-skeleton ww-skel-line" style="width:{widths[i % len(widths)]}%;"></span>'
        for i in range(lines)
    )
    st.markdown(
        f'<div class="ww-card" style="padding:1.75rem 2rem;display:flex;flex-direction:column;">'
        f'{header_html}{lines_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_tag(text: str, color: str = "ink") -> str:
    palettes = {
        "ink":     ("rgba(26,26,46,0.07)",   "rgba(26,26,46,0.65)"),
        "sunrise": ("rgba(255,107,107,0.10)", "#FF6B6B"),
        "amber":   ("rgba(255,171,64,0.12)",  "#B86E00"),
        "sky":     ("rgba(110,198,255,0.14)", "#2B8CC4"),
        # legacy aliases
        "fire":    ("rgba(255,107,107,0.10)", "#FF6B6B"),
        "purple":  ("rgba(26,26,46,0.07)",    "rgba(26,26,46,0.65)"),
        "blue":    ("rgba(110,198,255,0.14)", "#2B8CC4"),
        "red":     ("rgba(255,107,107,0.10)", "#FF6B6B"),
        "gray":    ("rgba(26,26,46,0.07)",    "rgba(26,26,46,0.45)"),
        "info":    ("rgba(26,26,46,0.07)",    "rgba(26,26,46,0.65)"),
        "success": ("rgba(110,198,255,0.14)", "#2B8CC4"),
        "warning": ("rgba(255,171,64,0.12)",  "#B86E00"),
    }
    bg, fg = palettes.get(color, palettes["ink"])
    return (
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'padding:0.2rem 0.7rem;border-radius:100px;font-size:0.78rem;'
        f'font-weight:500;margin:0.15rem 0.2rem 0.15rem 0;letter-spacing:0.01em;">{text}</span>'
    )


def render_badge(text: str, variant: str = "sunrise") -> str:
    palettes = {
        "sunrise": ("#FF6B6B", "#FFFFFF"),
        "amber":   ("#FFAB40", "#1A1A2E"),
        "sky":     ("#6EC6FF", "#1A1A2E"),
        "ink":     ("#1A1A2E", "#FFFBF5"),
        "ghost":   ("rgba(26,26,46,0.07)", "rgba(26,26,46,0.70)"),
        # legacy aliases
        "fire":    ("#FF6B6B", "#FFFFFF"),
        "purple":  ("#FF6B6B", "#FFFFFF"),
        "blue":    ("#6EC6FF", "#1A1A2E"),
        "red":     ("#FF6B6B", "#FFFFFF"),
        "gray":    ("rgba(26,26,46,0.07)", "rgba(26,26,46,0.45)"),
        "high":    ("#FF6B6B", "#FFFFFF"),
        "medium":  ("rgba(255,171,64,0.20)", "#B86E00"),
        "low":     ("rgba(26,26,46,0.06)", "rgba(26,26,46,0.40)"),
    }
    bg, fg = palettes.get(variant, palettes["ghost"])
    return (
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'padding:0.25rem 0.85rem;border-radius:100px;font-size:0.78rem;'
        f'font-weight:600;letter-spacing:0.01em;">{text}</span>'
    )


def render_info_box(message: str, color: str = "ink") -> None:
    if color in ("sunrise", "fire", "red", "warning"):
        bg = "rgba(255,107,107,0.08)"
        tc = "#FF6B6B"
        border = "rgba(255,107,107,0.18)"
    elif color in ("amber",):
        bg = "rgba(255,171,64,0.10)"
        tc = "#B86E00"
        border = "rgba(255,171,64,0.22)"
    elif color in ("sky", "blue", "info"):
        bg = "rgba(110,198,255,0.10)"
        tc = "#2B8CC4"
        border = "rgba(110,198,255,0.22)"
    elif color == "green":
        bg = "rgba(110,198,255,0.08)"
        tc = "rgba(26,26,46,0.65)"
        border = "rgba(110,198,255,0.15)"
    else:
        bg = "rgba(26,26,46,0.05)"
        tc = "rgba(26,26,46,0.65)"
        border = "rgba(26,26,46,0.10)"
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-radius:14px;'
        f'padding:1rem 1.25rem;margin:0.75rem 0;">'
        f'<span style="color:{tc};font-size:0.9rem;font-weight:500;line-height:1.6;">{message}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# Backwards-compatible aliases
def render_success_message(message: str) -> None:
    render_info_box(message, color="sky")

def render_warning_message(message: str) -> None:
    render_info_box(message, color="sunrise")

def render_info_message(message: str) -> None:
    render_info_box(message, color="ink")


def render_metric_card(value: str, label: str) -> None:
    st.markdown(
        f'<div class="ww-card" style="text-align:left;padding:1.75rem 2rem;">'
        f'<div style="font-family:\'Syne\',sans-serif;font-size:2.5rem;font-weight:700;'
        f'color:#1A1A2E;letter-spacing:-0.02em;line-height:1;">{value}</div>'
        f'<div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:0.09em;color:rgba(26,26,46,0.42);margin-top:0.5rem;">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
