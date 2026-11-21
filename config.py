"""
ChillGPT - Application Configuration and UI Themes
A Minimalist Creative Portfolio + Cute AI Companion Experience
Visual Identity: Warm Cream, Soft White, Lavender Accents, Playful Mascot "Chilly"
"""

import json
from pathlib import Path
from typing import List, Dict, Any

APP_TITLE = "ChillGPT"
APP_SUBTITLE = "Your Little AI Support Companion"
APP_TAGLINE = "Turn complaints into calm, policy-perfect solutions"
APP_ICON = "✨"

DATA_DIR = Path(__file__).parent / "data"
POLICIES_FILE = DATA_DIR / "sample_policies.json"
COMPLAINTS_FILE = DATA_DIR / "sample_complaints.json"


def load_sample_policies() -> List[Dict[str, Any]]:
    """Loads default pre-configured company policies."""
    if not POLICIES_FILE.exists():
        return []
    try:
        with open(POLICIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("policies", [])
    except Exception:
        return []


def load_sample_complaints() -> List[Dict[str, Any]]:
    """Loads default pre-configured test customer complaints."""
    if not COMPLAINTS_FILE.exists():
        return []
    try:
        with open(COMPLAINTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("complaints", [])
    except Exception:
        return []


def render_mascot_component(
    state: str = "idle",
    message: str = "Tell me what happened. I've got you.",
    theme: str = "light"
) -> str:
    """
    Renders Chilly, the cute animated mascot, inside a self-contained HTML iframe.
    This guarantees 100% immune rendering from Streamlit Markdown code block parsing.
    States: 'idle', 'listening', 'typing', 'generating', 'success', 'warning'
    """
    is_dark = (theme == "dark")

    # Body Gradient Colors
    if is_dark:
        bg_card = "#1B1C22"
        text_color = "#F5F3EF"
        border_color = "rgba(255, 255, 255, 0.12)"
        grad_start = "#7C3AED"
        grad_mid = "#6D28D9"
        grad_end = "#5B21B6"
        stroke_color = "rgba(255, 255, 255, 0.18)"
        face_feature = "#F5F3EF"
        blush_color = "#F472B6"
        hand_color = "#8B5CF6"
        star_color = "#FDE047"
    else:
        bg_card = "#FFFFFF"
        text_color = "#262422"
        border_color = "rgba(0, 0, 0, 0.08)"
        grad_start = "#F5F3FF"
        grad_mid = "#EDE9FE"
        grad_end = "#E0E7FF"
        stroke_color = "rgba(139, 92, 246, 0.22)"
        face_feature = "#262422"
        blush_color = "#F472B6"
        hand_color = "#DDD6FE"
        star_color = "#F59E0B"

    # Eyes & Mouth based on state
    if state == "generating":
        eyes_svg = f"""
        <g class="sparkle-eyes">
            <text x="54" y="82" font-size="16" fill="{grad_start if is_dark else '#8B5CF6'}" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif">✦</text>
            <text x="106" y="82" font-size="16" fill="{grad_start if is_dark else '#8B5CF6'}" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif">✦</text>
        </g>
        <path d="M 75,86 Q 80,91 85,86" stroke="{face_feature}" stroke-width="2.5" stroke-linecap="round" fill="none"/>
        """
    elif state in ("success", "compliant"):
        eyes_svg = f"""
        <g class="happy-eyes">
            <path d="M 52,78 Q 60,70 68,78" stroke="{face_feature}" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M 92,78 Q 100,70 108,78" stroke="{face_feature}" stroke-width="3" stroke-linecap="round" fill="none"/>
        </g>
        <path d="M 74,83 Q 80,92 86,83 Z" fill="{face_feature}"/>
        """
    elif state in ("warning", "review"):
        eyes_svg = f"""
        <g class="curious-eyes">
            <circle cx="60" cy="75" r="5.5" fill="{face_feature}"/>
            <circle cx="58.5" cy="73" r="1.8" fill="#FFFFFF"/>
            <circle cx="100" cy="75" r="5.5" fill="{face_feature}"/>
            <circle cx="98.5" cy="73" r="1.8" fill="#FFFFFF"/>
        </g>
        <ellipse cx="80" cy="86" rx="3" ry="4" fill="{face_feature}"/>
        """
    else:  # idle, listening, typing
        eyes_svg = f"""
        <g class="normal-eyes">
            <g class="eye-left">
                <circle cx="60" cy="75" r="6" fill="{face_feature}"/>
                <circle cx="58" cy="73" r="2.2" fill="#FFFFFF"/>
                <circle cx="62" cy="77" r="1" fill="#FFFFFF"/>
            </g>
            <g class="eye-right">
                <circle cx="100" cy="75" r="6" fill="{face_feature}"/>
                <circle cx="98" cy="73" r="2.2" fill="#FFFFFF"/>
                <circle cx="102" cy="77" r="1" fill="#FFFFFF"/>
            </g>
        </g>
        <path d="M 75,85 Q 80,90 85,85" stroke="{face_feature}" stroke-width="2.5" stroke-linecap="round" fill="none"/>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700&display=swap');
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}
body {{
    background: transparent;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Plus Jakarta Sans', sans-serif;
    overflow: hidden;
    height: 100vh;
}}
.speech-bubble {{
    background: {bg_card};
    color: {text_color};
    border: 1px solid {border_color};
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 0.92rem;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
    margin-bottom: 8px;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    position: relative;
    animation: bubbleIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}}
.speech-bubble::after {{
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid {bg_card};
}}
.bubble-star {{
    color: #A78BFA;
    font-size: 0.82rem;
}}
.character-wrap {{
    animation: floatAnim 4.2s ease-in-out infinite;
    transform-origin: center bottom;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.chilly-body {{
    animation: breatheAnim 3.8s ease-in-out infinite alternate;
    transform-origin: 80px 80px;
}}
.normal-eyes {{
    animation: blinkAnim 4.2s infinite;
    transform-origin: 80px 75px;
}}
.chilly-halo-star {{
    animation: starSpin 3s ease-in-out infinite alternate;
    transform-origin: 80px 17px;
}}
@keyframes floatAnim {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-7px); }}
}}
@keyframes breatheAnim {{
    0% {{ transform: scale(1); }}
    100% {{ transform: scale(1.025, 0.985); }}
}}
@keyframes blinkAnim {{
    0%, 92%, 100% {{ transform: scaleY(1); }}
    96% {{ transform: scaleY(0.1); }}
}}
@keyframes starSpin {{
    0% {{ transform: rotate(-8deg) scale(0.95); }}
    100% {{ transform: rotate(12deg) scale(1.08); }}
}}
@keyframes bubbleIn {{
    0% {{ opacity: 0; transform: translateY(4px) scale(0.96); }}
    100% {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
</style>
</head>
<body>
    <div class="speech-bubble">
        <span class="bubble-star">✦</span>
        <span>{message}</span>
    </div>
    <div class="character-wrap">
        <svg class="chilly-svg" width="150" height="135" viewBox="0 0 160 150" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="chillyBodyGrad" x1="20" y1="20" x2="140" y2="140" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stop-color="{grad_start}"/>
                    <stop offset="50%" stop-color="{grad_mid}"/>
                    <stop offset="100%" stop-color="{grad_end}"/>
                </linearGradient>
                <filter id="chillySoftShadow" x="-10" y="-10" width="180" height="180" filterUnits="userSpaceOnUse">
                    <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="rgba(139, 92, 246, 0.20)"/>
                </filter>
            </defs>
            <g class="chilly-halo-star">
                <path d="M 80,12 Q 80,17 85,17 Q 80,17 80,22 Q 80,17 75,17 Q 80,17 80,12 Z" fill="{star_color}"/>
            </g>
            <path class="chilly-body" d="M 45,52 C 45,30 65,22 80,22 C 95,22 115,30 115,52 C 124,58 132,70 132,86 C 132,106 116,122 96,124 C 88,125 72,125 64,124 C 44,122 28,106 28,86 C 28,70 36,58 45,52 Z" 
                  fill="url(#chillyBodyGrad)" stroke="{stroke_color}" stroke-width="1.5" filter="url(#chillySoftShadow)"/>
            <ellipse cx="48" cy="85" rx="7" ry="4" fill="{blush_color}" opacity="0.45"/>
            <ellipse cx="112" cy="85" rx="7" ry="4" fill="{blush_color}" opacity="0.45"/>
            {eyes_svg}
            <ellipse cx="32" cy="90" rx="5" ry="7.5" fill="{hand_color}" transform="rotate(-15 32 90)"/>
            <ellipse cx="128" cy="90" rx="5" ry="7.5" fill="{hand_color}" transform="rotate(15 128 90)"/>
        </svg>
    </div>
</body>
</html>"""
    return html


def get_custom_css(theme: str = "light") -> str:
    """
    Minimalist Creative Portfolio + Cute AI Companion Stylesheet.
    Warm Cream / Midnight Charcoal, soft rounded surfaces, subtle pastel accents.
    """
    is_dark = (theme == "dark")

    if is_dark:
        bg_main = "#121316"
        bg_card = "#1A1C22"
        bg_card_alt = "#23262E"
        bg_sidebar = "#15171C"
        text_primary = "#F5F3EF"
        text_secondary = "#B8B4AE"
        text_muted = "#7A7772"
        border_color = "rgba(255, 255, 255, 0.08)"
        border_strong = "rgba(255, 255, 255, 0.16)"
        accent_lavender = "#A78BFA"
        accent_lavender_subtle = "rgba(167, 139, 250, 0.14)"
        accent_peach = "#FDBA74"
        accent_butter = "#FDE047"
        status_compliant_bg = "rgba(16, 185, 129, 0.12)"
        status_compliant_text = "#6EE7B7"
        status_compliant_border = "rgba(16, 185, 129, 0.3)"
        status_warning_bg = "rgba(245, 158, 11, 0.12)"
        status_warning_text = "#FCD34D"
        status_warning_border = "rgba(245, 158, 11, 0.3)"
        status_danger_bg = "rgba(244, 63, 94, 0.12)"
        status_danger_text = "#FDA4AF"
        status_danger_border = "rgba(244, 63, 94, 0.3)"
        input_bg = "#1A1C22"
        shadow_soft = "0 4px 20px rgba(0, 0, 0, 0.3)"
        shadow_float = "0 12px 32px rgba(0, 0, 0, 0.45)"
    else:
        bg_main = "#FAF7F2"
        bg_card = "#FFFFFF"
        bg_card_alt = "#F6F3EC"
        bg_sidebar = "#F5F2EB"
        text_primary = "#262422"
        text_secondary = "#6E6A66"
        text_muted = "#9C9791"
        border_color = "rgba(0, 0, 0, 0.07)"
        border_strong = "rgba(0, 0, 0, 0.14)"
        accent_lavender = "#8B5CF6"
        accent_lavender_subtle = "#EDE9FE"
        accent_peach = "#FDBA74"
        accent_butter = "#FDE047"
        status_compliant_bg = "#ECFDF5"
        status_compliant_text = "#047857"
        status_compliant_border = "#A7F3D0"
        status_warning_bg = "#FFFBEB"
        status_warning_text = "#B45309"
        status_warning_border = "#FDE68A"
        status_danger_bg = "#FFF1F2"
        status_danger_text = "#BE123C"
        status_danger_border = "#FECDD3"
        input_bg = "#FFFFFF"
        shadow_soft = "0 4px 20px rgba(0, 0, 0, 0.04)"
        shadow_float = "0 14px 34px -4px rgba(0, 0, 0, 0.07)"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
    --bg-main: {bg_main};
    --bg-card: {bg_card};
    --bg-card-alt: {bg_card_alt};
    --bg-sidebar: {bg_sidebar};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-muted: {text_muted};
    --border-color: {border_color};
    --border-strong: {border_strong};
    --accent-lavender: {accent_lavender};
    --accent-lavender-subtle: {accent_lavender_subtle};
    --accent-peach: {accent_peach};
    --accent-butter: {accent_butter};
    --status-compliant-bg: {status_compliant_bg};
    --status-compliant-text: {status_compliant_text};
    --status-compliant-border: {status_compliant_border};
    --status-warning-bg: {status_warning_bg};
    --status-warning-text: {status_warning_text};
    --status-warning-border: {status_warning_border};
    --status-danger-bg: {status_danger_bg};
    --status-danger-text: {status_danger_text};
    --status-danger-border: {status_danger_border};
    --input-bg: {input_bg};
    --shadow-soft: {shadow_soft};
    --shadow-float: {shadow_float};
}}

/* Respect Reduced Motion Preferences */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}

/* Subtle Keyframes */
@keyframes fadeInScale {{
    0% {{
        opacity: 0;
        transform: translateY(8px);
    }}
    100% {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* Global Canvas */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

/* Streamlit Block Container spacing */
.main .block-container {{
    max-width: 1040px;
    padding-top: 1.2rem;
    padding-bottom: 3.5rem;
}}

/* Sidebar Overrides */
[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Playfair Display', Georgia, serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
}}

p, span, div, label {{
    font-size: 1.02rem;
}}

/* Portfolio Top Navigation Bar */
.portfolio-pill-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 8px;
    border-radius: 999px;
    background: var(--accent-lavender-subtle);
    color: var(--accent-lavender);
    border: 1px solid var(--border-color);
}}

/* Hero Section */
.hero-editorial {{
    text-align: center;
    margin-bottom: 22px;
}}
.hero-tagline {{
    font-size: 0.84rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent-lavender);
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
}}
.hero-heading {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.1rem, 4.5vw, 3rem);
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    margin-bottom: 12px;
}}
.hero-sub {{
    font-size: 1.05rem;
    color: var(--text-secondary);
    max-width: 540px;
    margin: 0 auto 16px auto;
    line-height: 1.6;
}}

/* Primary Action Buttons */
.stButton > button[kind="primary"] {{
    background: var(--text-primary) !important;
    color: var(--bg-main) !important;
    border: none !important;
    border-radius: 999px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.02rem !important;
    padding: 13px 32px !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-float) !important;
    background: var(--accent-lavender) !important;
    color: #FFFFFF !important;
}}
.stButton > button[kind="primary"]:active {{
    transform: translateY(1px) !important;
}}

.stButton > button:not([kind="primary"]) {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 999px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    padding: 10px 22px !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:not([kind="primary"]):hover {{
    border-color: var(--accent-lavender) !important;
    color: var(--accent-lavender) !important;
    transform: translateY(-1px) !important;
}}

/* Soft Tone Selector Pills */
[data-testid="stRadio"] > div {{
    gap: 10px !important;
    justify-content: center !important;
}}
[data-testid="stRadio"] label {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    padding: 9px 20px !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    color: var(--text-secondary) !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: var(--accent-lavender) !important;
    color: var(--accent-lavender) !important;
}}

/* Form Inputs (Text Area) */
.stTextArea textarea {{
    background-color: var(--input-bg) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border-color) !important;
    border-radius: 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
    padding: 16px 18px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    box-shadow: var(--shadow-soft) !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--accent-lavender) !important;
    box-shadow: 0 0 0 3px var(--accent-lavender-subtle) !important;
}}

/* Minimal Creative Resolution Reading Card */
.reading-canvas {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 24px;
    padding: 30px 34px;
    box-shadow: var(--shadow-float);
    margin: 22px 0;
    animation: fadeInScale 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}}
.reading-canvas-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 16px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}}
.reading-canvas-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.reading-canvas-body {{
    font-size: 1.15rem;
    line-height: 1.8;
    color: var(--text-primary);
    white-space: pre-wrap;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 450;
}}

/* Status Indicator Badges */
.status-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}}
.chip-compliant {{
    background: var(--status-compliant-bg);
    color: var(--status-compliant-text);
    border: 1px solid var(--status-compliant-border);
}}
.chip-partially {{
    background: var(--status-warning-bg);
    color: var(--status-warning-text);
    border: 1px solid var(--status-warning-border);
}}
.chip-noncompliant {{
    background: var(--status-danger-bg);
    color: var(--status-danger-text);
    border: 1px solid var(--status-danger-border);
}}

/* Alert Containers */
.alert-container-danger {{
    background: var(--status-danger-bg);
    border-left: 3px solid #E11D48;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    color: var(--status-danger-text);
    font-size: 0.96rem;
    margin-bottom: 10px;
}}
.alert-container-warning {{
    background: var(--status-warning-bg);
    border-left: 3px solid #D97706;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    color: var(--status-warning-text);
    font-size: 0.96rem;
    margin-bottom: 10px;
}}
.alert-container-success {{
    background: var(--status-compliant-bg);
    border-left: 3px solid #059669;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    color: var(--status-compliant-text);
    font-size: 0.96rem;
    margin-bottom: 10px;
}}

/* Minimal Metric Tile */
.metric-tile {{
    background: var(--bg-card-alt);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 16px 18px;
    height: 100%;
}}
.metric-tile-label {{
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 5px;
}}
.metric-tile-value {{
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
}}

/* Tone Scores Visual Progress */
.tone-metric-row {{
    background: var(--bg-card-alt);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 14px 16px;
    text-align: center;
}}
.tone-score-num {{
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--accent-lavender);
    font-family: 'JetBrains Mono', monospace;
}}
.tone-score-tag {{
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 3px;
}}

/* Tabs Styling */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 8px !important;
    background: var(--bg-card) !important;
    padding: 6px !important;
    border-radius: 999px !important;
    border: 1px solid var(--border-color) !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    border-radius: 999px !important;
    padding: 8px 20px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: var(--text-muted) !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background: var(--text-primary) !important;
    color: var(--bg-main) !important;
}}

/* Expanders */
.streamlit-expanderHeader {{
    border-radius: 14px !important;
    border: 1px solid var(--border-color) !important;
    background: var(--bg-card) !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
    transition: all 0.15s ease !important;
}}
.streamlit-expanderHeader:hover {{
    background: var(--bg-card-alt) !important;
}}

/* Minimal Portfolio Footer */
.portfolio-footer {{
    border-top: 1px solid var(--border-color);
    padding: 28px 0 16px 0;
    margin-top: 56px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--text-muted);
    flex-wrap: wrap;
    gap: 12px;
}}
.portfolio-footer-brand {{
    font-weight: 600;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
}}
</style>
"""
    return css
