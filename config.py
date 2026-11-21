"""
ChillGPT - Application Configuration, Mascot & UI Themes
Visual Identity: Minimalist Creative Portfolio + Cute AI Companion
Color Palette: Warm Cream, Soft White, Lavender, Butter Yellow, Peach, Charcoal
"""

import json
from pathlib import Path
from typing import List, Dict, Any

APP_TITLE = "ChillGPT"
APP_SUBTITLE = "Your Little AI Support Companion"
APP_TAGLINE = "Let's make things a little better."
APP_ICON = "✨"

DATA_DIR = Path(__file__).parent / "data"
POLICIES_FILE = DATA_DIR / "sample_policies.json"
COMPLAINTS_FILE = DATA_DIR / "sample_complaints.json"


def load_sample_policies() -> List[Dict[str, Any]]:
    """Loads pre-configured company policies."""
    if not POLICIES_FILE.exists():
        return []
    try:
        with open(POLICIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("policies", [])
    except Exception:
        return []


def load_sample_complaints() -> List[Dict[str, Any]]:
    """Loads pre-configured test customer complaints."""
    if not COMPLAINTS_FILE.exists():
        return []
    try:
        with open(COMPLAINTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("complaints", [])
    except Exception:
        return []


def render_mascot_svg(state: str = "idle", message: str = "Tell me what happened. I've got you.", theme: str = "light") -> str:
    """
    Renders Chilly, the cute ChillGPT mascot with smooth CSS animations,
    expressive eyes, soft blushes, and a floating speech bubble.
    States: 'idle', 'typing', 'generating', 'success', 'warning'
    """
    is_dark = (theme == "dark")

    # Body Gradient Colors
    if is_dark:
        grad_start = "#6D28D9"
        grad_mid = "#5B21B6"
        grad_end = "#4C1D95"
        stroke_color = "rgba(255, 255, 255, 0.15)"
        face_feature = "#F5F3EF"
        blush_color = "#F472B6"
        hand_color = "#7C3AED"
        star_color = "#FDE047"
    else:
        grad_start = "#F5F3FF"
        grad_mid = "#EDE9FE"
        grad_end = "#E0E7FF"
        stroke_color = "rgba(139, 92, 246, 0.18)"
        face_feature = "#2D2B2A"
        blush_color = "#F472B6"
        hand_color = "#DDD6FE"
        star_color = "#F59E0B"

    # Eyes & Mouth based on state
    if state == "generating":
        eyes_svg = f"""
        <g class="chilly-sparkle-eyes">
            <text x="54" y="82" font-size="16" fill="{grad_start if is_dark else '#8B5CF6'}" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif">✦</text>
            <text x="106" y="82" font-size="16" fill="{grad_start if is_dark else '#8B5CF6'}" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif">✦</text>
        </g>
        <path d="M 75,86 Q 80,91 85,86" stroke="{face_feature}" stroke-width="2.5" stroke-linecap="round" fill="none"/>
        """
    elif state in ("success", "compliant"):
        eyes_svg = f"""
        <g class="chilly-happy-eyes">
            <path d="M 52,78 Q 60,70 68,78" stroke="{face_feature}" stroke-width="3" stroke-linecap="round" fill="none"/>
            <path d="M 92,78 Q 100,70 108,78" stroke="{face_feature}" stroke-width="3" stroke-linecap="round" fill="none"/>
        </g>
        <path d="M 74,83 Q 80,92 86,83 Z" fill="{face_feature}"/>
        """
    elif state in ("warning", "review"):
        eyes_svg = f"""
        <g class="chilly-curious-eyes">
            <circle cx="60" cy="75" r="5.5" fill="{face_feature}"/>
            <circle cx="58.5" cy="73" r="1.8" fill="#FFFFFF"/>
            <circle cx="100" cy="75" r="5.5" fill="{face_feature}"/>
            <circle cx="98.5" cy="73" r="1.8" fill="#FFFFFF"/>
        </g>
        <ellipse cx="80" cy="86" rx="3" ry="4" fill="{face_feature}"/>
        """
    else:  # idle, typing, default
        eyes_svg = f"""
        <g class="chilly-normal-eyes">
            <g class="chilly-eye-left">
                <circle cx="60" cy="75" r="6" fill="{face_feature}"/>
                <circle cx="58" cy="73" r="2.2" fill="#FFFFFF"/>
                <circle cx="62" cy="77" r="1" fill="#FFFFFF"/>
            </g>
            <g class="chilly-eye-right">
                <circle cx="100" cy="75" r="6" fill="{face_feature}"/>
                <circle cx="98" cy="73" r="2.2" fill="#FFFFFF"/>
                <circle cx="102" cy="77" r="1" fill="#FFFFFF"/>
            </g>
        </g>
        <path d="M 75,85 Q 80,90 85,85" stroke="{face_feature}" stroke-width="2.5" stroke-linecap="round" fill="none"/>
        """

    svg_markup = f"""
    <div class="mascot-stage">
        <div class="mascot-speech-bubble">
            <span class="speech-star">✦</span>
            <span class="speech-text">{message}</span>
        </div>
        <div class="mascot-character-wrap">
            <svg class="chilly-svg" width="160" height="150" viewBox="0 0 160 150" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="chillyBodyGrad" x1="20" y1="20" x2="140" y2="140" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="{grad_start}"/>
                        <stop offset="50%" stop-color="{grad_mid}"/>
                        <stop offset="100%" stop-color="{grad_end}"/>
                    </linearGradient>
                    <filter id="chillySoftShadow" x="-10" y="-10" width="180" height="180" filterUnits="userSpaceOnUse">
                        <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="rgba(139, 92, 246, 0.22)"/>
                    </filter>
                </defs>

                <!-- Floating Star on Head -->
                <g class="chilly-halo-star">
                    <path d="M 80,12 Q 80,17 85,17 Q 80,17 80,22 Q 80,17 75,17 Q 80,17 80,12 Z" fill="{star_color}"/>
                </g>

                <!-- Soft Blob Body -->
                <path class="chilly-body" d="M 45,52 C 45,30 65,22 80,22 C 95,22 115,30 115,52 C 124,58 132,70 132,86 C 132,106 116,122 96,124 C 88,125 72,125 64,124 C 44,122 28,106 28,86 C 28,70 36,58 45,52 Z" 
                      fill="url(#chillyBodyGrad)" stroke="{stroke_color}" stroke-width="1.5" filter="url(#chillySoftShadow)"/>

                <!-- Rosy Cheeks -->
                <ellipse cx="48" cy="85" rx="7" ry="4" fill="{blush_color}" opacity="0.45"/>
                <ellipse cx="112" cy="85" rx="7" ry="4" fill="{blush_color}" opacity="0.45"/>

                <!-- Eyes and Mouth -->
                {eyes_svg}

                <!-- Cute Tiny Floating Arms -->
                <ellipse cx="32" cy="90" rx="5" ry="7.5" fill="{hand_color}" transform="rotate(-15 32 90)"/>
                <ellipse cx="128" cy="90" rx="5" ry="7.5" fill="{hand_color}" transform="rotate(15 128 90)"/>
            </svg>
        </div>
    </div>
    """
    return svg_markup


def get_custom_css(theme: str = "light") -> str:
    """
    Minimalist Creative Portfolio + Cute AI Companion Stylesheet.
    Warm Cream / Midnight Studio, soft rounded surfaces, subtle pastel accents.
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
        accent_butter = "#FDE68A"
        accent_mint = "#34D399"
        accent_rose = "#F472B6"
        status_compliant_bg = "rgba(52, 211, 153, 0.12)"
        status_compliant_text = "#6EE7B7"
        status_compliant_border = "rgba(52, 211, 153, 0.3)"
        status_warning_bg = "rgba(251, 191, 36, 0.12)"
        status_warning_text = "#FCD34D"
        status_warning_border = "rgba(251, 191, 36, 0.3)"
        status_danger_bg = "rgba(244, 63, 94, 0.12)"
        status_danger_text = "#FDA4AF"
        status_danger_border = "rgba(244, 63, 94, 0.3)"
        input_bg = "#16181D"
        shadow_soft = "0 10px 30px rgba(0, 0, 0, 0.4)"
        shadow_float = "0 18px 48px rgba(0, 0, 0, 0.55)"
    else:
        bg_main = "#FAF8F5"       # Warm Cream Canvas
        bg_card = "#FFFFFF"       # Pure White Surface
        bg_card_alt = "#F5F1EA"   # Delicate Cream Tint
        bg_sidebar = "#F4EFE6"
        text_primary = "#2D2B2A"   # Rich Charcoal
        text_secondary = "#6B6764" # Warm Graphite
        text_muted = "#9E9893"     # Soft Taupe
        border_color = "rgba(45, 43, 42, 0.07)"
        border_strong = "rgba(45, 43, 42, 0.14)"
        accent_lavender = "#7C3AED"
        accent_lavender_subtle = "#F3E8FF"
        accent_butter = "#FEF3C7"
        accent_mint = "#D1FAE5"
        accent_rose = "#FCE7F3"
        status_compliant_bg = "#ECFDF5"
        status_compliant_text = "#065F46"
        status_compliant_border = "#A7F3D0"
        status_warning_bg = "#FFFBEB"
        status_warning_text = "#92400E"
        status_warning_border = "#FDE68A"
        status_danger_bg = "#FFF1F2"
        status_danger_text = "#9F1239"
        status_danger_border = "#FECDD3"
        input_bg = "#FFFFFF"
        shadow_soft = "0 8px 24px rgba(45, 43, 42, 0.04), 0 2px 6px rgba(45, 43, 42, 0.02)"
        shadow_float = "0 16px 36px rgba(45, 43, 42, 0.06), 0 4px 12px rgba(45, 43, 42, 0.03)"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=JetBrains+Mono:wght@400;500&display=swap');

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
    --accent-butter: {accent_butter};
    --accent-mint: {accent_mint};
    --accent-rose: {accent_rose};
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

/* Accessibility: Reduced Motion */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}

/* Keyframes for Mascot & Fluid Micro-Interactions */
@keyframes chillyFloat {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-8px) rotate(1.5deg); }}
}}

@keyframes chillyBreathe {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.02, 0.98); }}
}}

@keyframes chillyBlink {{
    0%, 90%, 100% {{ transform: scaleY(1); }}
    95% {{ transform: scaleY(0.08); }}
}}

@keyframes chillyStarSpin {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-3px) rotate(18deg); }}
}}

@keyframes fadeInScale {{
    0% {{ opacity: 0; transform: translateY(8px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

/* Global Application Canvas */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

.main .block-container {{
    max-width: 1040px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}}

/* Typography */
h1, h2, h3 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: var(--text-primary) !important;
}}

/* Creative Portfolio Top Navigation */
.portfolio-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 999px;
    box-shadow: var(--shadow-soft);
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    transition: all 0.2s ease;
}}
.portfolio-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.portfolio-logo {{
    width: 32px;
    height: 32px;
    background: var(--accent-lavender-subtle);
    color: var(--accent-lavender);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    font-weight: 700;
}}
.portfolio-title {{
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);
}}
.portfolio-pill-badge {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 4px 10px;
    background: var(--bg-card-alt);
    border-radius: 999px;
    color: var(--text-muted);
}}

/* Central Mascot Stage */
.mascot-stage {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 18px auto 26px auto;
    text-align: center;
}}
.mascot-speech-bubble {{
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    padding: 9px 20px;
    border-radius: 999px;
    font-size: 0.94rem;
    font-weight: 600;
    box-shadow: var(--shadow-soft);
    margin-bottom: 12px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    position: relative;
    animation: fadeInScale 0.3s ease;
}}
.mascot-speech-bubble::after {{
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid var(--bg-card);
}}
.speech-star {{
    color: var(--accent-lavender);
    font-size: 0.85rem;
}}
.mascot-character-wrap {{
    animation: chillyFloat 4.2s ease-in-out infinite;
    transform-origin: center bottom;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.chilly-svg {{
    overflow: visible;
}}
.chilly-body {{
    animation: chillyBreathe 3.6s ease-in-out infinite alternate;
    transform-origin: 80px 80px;
}}
.chilly-normal-eyes {{
    animation: chillyBlink 4.5s infinite;
    transform-origin: 80px 75px;
}}
.chilly-halo-star {{
    animation: chillyStarSpin 3s ease-in-out infinite alternate;
    transform-origin: 80px 17px;
}}

/* Hero Section */
.hero-editorial {{
    text-align: center;
    margin-bottom: 24px;
}}
.hero-tagline {{
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent-lavender);
    margin-bottom: 8px;
}}
.hero-heading {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2rem, 4vw, 2.8rem);
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    margin-bottom: 8px;
}}
.hero-sub {{
    font-size: 1.02rem;
    color: var(--text-secondary);
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.5;
}}

/* Form Inputs (Minimal, Soft, Pillowed) */
.stTextArea textarea {{
    background-color: var(--input-bg) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border-color) !important;
    border-radius: 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
    padding: 16px 18px !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.2s ease !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--accent-lavender) !important;
    box-shadow: 0 0 0 4px var(--accent-lavender-subtle) !important;
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
    padding: 13px 30px !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-float) !important;
    background: var(--accent-lavender) !important;
    color: #FFFFFF !important;
}}

.stButton > button:not([kind="primary"]) {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 10px 20px !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:not([kind="primary"]):hover {{
    border-color: var(--accent-lavender) !important;
    color: var(--accent-lavender) !important;
}}

/* Soft Tone Selector Pills */
[data-testid="stRadio"] > div {{
    gap: 8px !important;
    justify-content: center !important;
}}
[data-testid="stRadio"] label {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    padding: 8px 18px !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    color: var(--text-secondary) !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: var(--accent-lavender) !important;
    color: var(--accent-lavender) !important;
}}

/* Minimal Creative Resolution Reading Card */
.reading-canvas {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 24px;
    padding: 32px 36px;
    box-shadow: var(--shadow-float);
    margin: 22px 0;
    animation: fadeInScale 0.3s ease;
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
    font-weight: 400;
}}

/* Soft Status Badges */
.pill-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}}
.pill-compliant {{
    background: var(--status-compliant-bg);
    color: var(--status-compliant-text);
    border: 1px solid var(--status-compliant-border);
}}
.pill-warning {{
    background: var(--status-warning-bg);
    color: var(--status-warning-text);
    border: 1px solid var(--status-warning-border);
}}
.pill-danger {{
    background: var(--status-danger-bg);
    color: var(--status-danger-text);
    border: 1px solid var(--status-danger-border);
}}

/* Soft Alert Callouts */
.soft-callout {{
    border-radius: 14px;
    padding: 14px 18px;
    font-size: 0.94rem;
    line-height: 1.6;
    margin-bottom: 10px;
}}
.callout-success {{
    background: var(--status-compliant-bg);
    border: 1px solid var(--status-compliant-border);
    color: var(--status-compliant-text);
}}
.callout-warning {{
    background: var(--status-warning-bg);
    border: 1px solid var(--status-warning-border);
    color: var(--status-warning-text);
}}
.callout-danger {{
    background: var(--status-danger-bg);
    border: 1px solid var(--status-danger-border);
    color: var(--status-danger-text);
}}

/* Tone Progress Bars */
.tone-score-card {{
    background: var(--bg-card-alt);
    border-radius: 14px;
    padding: 12px 14px;
    text-align: center;
    border: 1px solid var(--border-color);
}}
.tone-score-val {{
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--accent-lavender);
    font-family: 'JetBrains Mono', monospace;
}}
.tone-score-lbl {{
    font-size: 0.74rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 2px;
}}

/* Tabs in Portfolio Style */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 8px !important;
    background: var(--bg-card) !important;
    padding: 6px !important;
    border-radius: 999px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-soft) !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    border-radius: 999px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: var(--text-muted) !important;
    transition: all 0.2s ease !important;
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
    font-size: 0.95rem !important;
    box-shadow: var(--shadow-soft) !important;
}}

/* Minimalist Portfolio Footer */
.portfolio-footer {{
    text-align: center;
    padding: 36px 0 12px 0;
    margin-top: 48px;
    border-top: 1px solid var(--border-color);
    font-size: 0.82rem;
    color: var(--text-muted);
}}
.portfolio-footer-brand {{
    font-weight: 700;
    color: var(--text-secondary);
    margin-bottom: 4px;
}}
</style>
"""
    return css
