"""
ChillGPT - Application Configuration and UI Themes
Visual Identity: Comic-Book Pop Art × Editorial Collage × Gen-Z Creative Studio
"""

import json
from pathlib import Path
from typing import List, Dict, Any

APP_TITLE = "CHILLGPT"
APP_TAGLINE = "COMPLAINTS, BUT MAKE IT CHILL."
APP_STUDIO_LABEL = "AI CUSTOMER SUPPORT STUDIO ✦"
APP_ICON = "⚡"

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


def get_custom_css(theme: str = "light") -> str:
    """
    Generates dynamic CSS for Light & Dark mode inspired by:
    Comic-book pop art, contemporary editorial collage, and Gen-Z creative branding.
    """
    is_dark = (theme == "dark")

    if is_dark:
        bg_main = "#121316"
        bg_panel = "#1C1E24"
        bg_panel_alt = "#242731"
        bg_sidebar = "#17181E"
        text_primary = "#F8F9FA"
        text_secondary = "#D5D8E0"
        text_muted = "#9BA1B0"
        border_color = "#E2E8F0"
        shadow_color = "#000000"
        input_bg = "#232630"
        halftone_color = "rgba(255, 255, 255, 0.04)"
        badge_bg = "#2A2D3A"
        hero_gradient = "linear-gradient(135deg, #1C1E24 0%, #292D39 100%)"
        accent_blue = "#2563EB"
        accent_yellow = "#FFDE00"
        accent_pink = "#FF007F"
        accent_orange = "#FF5500"
        accent_cyan = "#00F0FF"
        accent_green = "#10B981"
    else:
        bg_main = "#FAF7F2"
        bg_panel = "#FFFFFF"
        bg_panel_alt = "#FFFDF9"
        bg_sidebar = "#F4F0E8"
        text_primary = "#111111"
        text_secondary = "#333333"
        text_muted = "#666666"
        border_color = "#111111"
        shadow_color = "#111111"
        input_bg = "#FFFFFF"
        halftone_color = "rgba(0, 0, 0, 0.04)"
        badge_bg = "#EFECE4"
        hero_gradient = "linear-gradient(135deg, #FFF9ED 0%, #FFF3D6 100%)"
        accent_blue = "#0F47FF"
        accent_yellow = "#FFE500"
        accent_pink = "#FF007F"
        accent_orange = "#FF5500"
        accent_cyan = "#00E5FF"
        accent_green = "#00C853"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {{
    --bg-main: {bg_main};
    --bg-panel: {bg_panel};
    --bg-panel-alt: {bg_panel_alt};
    --bg-sidebar: {bg_sidebar};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-muted: {text_muted};
    --border-color: {border_color};
    --shadow-color: {shadow_color};
    --input-bg: {input_bg};
    --accent-blue: {accent_blue};
    --accent-yellow: {accent_yellow};
    --accent-pink: {accent_pink};
    --accent-orange: {accent_orange};
    --accent-cyan: {accent_cyan};
    --accent-green: {accent_green};
}}

/* Global Reset & Comic Halftone Background */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--bg-main) !important;
    background-image: radial-gradient({halftone_color} 1.5px, transparent 1.5px) !important;
    background-size: 16px 16px !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}}

/* Sidebar Customization */
[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 3px solid var(--border-color) !important;
}}

/* Headings font */
h1, h2, h3, h4, h5, h6, .brand-title, .panel-title {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: var(--text-primary) !important;
}}

/* Top Navigation Bar */
.top-nav-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0 20px 0;
    margin-bottom: 10px;
    border-bottom: 2.5px solid var(--border-color);
}}
.nav-brand-group {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.nav-badge {{
    background: var(--accent-yellow);
    color: #111111;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 0.72rem;
    padding: 4px 10px;
    border: 2px solid var(--border-color);
    box-shadow: 2px 2px 0px var(--shadow-color);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: inline-block;
    transform: rotate(-1.5deg);
}}
.brand-wordmark {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 900;
    font-size: 1.7rem;
    letter-spacing: -0.04em;
    color: var(--text-primary);
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.brand-wordmark span.chill {{
    background: var(--accent-blue);
    color: #FFFFFF;
    padding: 2px 8px;
    border: 2px solid var(--border-color);
    box-shadow: 2px 2px 0px var(--shadow-color);
}}

/* Hero Section */
.hero-box {{
    background: {hero_gradient};
    border: 3px solid var(--border-color);
    box-shadow: 6px 6px 0px var(--shadow-color);
    padding: 26px 30px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}}
.hero-box::before {{
    content: "⚡";
    position: absolute;
    right: 20px;
    bottom: -15px;
    font-size: 7rem;
    opacity: 0.08;
    pointer-events: none;
}}
.hero-tag {{
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent-pink);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 900;
    line-height: 1.05;
    margin: 0 0 10px 0;
    letter-spacing: -0.04em;
    color: var(--text-primary);
}}
.hero-highlight {{
    background: var(--accent-yellow);
    color: #111111;
    padding: 2px 10px;
    border: 2px solid var(--border-color);
    display: inline-block;
    box-shadow: 3px 3px 0px var(--shadow-color);
    transform: rotate(0.8deg);
}}
.hero-sub {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.02rem;
    color: var(--text-secondary);
    margin: 0;
    font-weight: 500;
}}

/* Comic Panels / Containers */
.comic-panel {{
    background: var(--bg-panel);
    border: 3px solid var(--border-color);
    box-shadow: 5px 5px 0px var(--shadow-color);
    padding: 20px;
    margin-bottom: 22px;
    position: relative;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.comic-panel-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 10px;
}}
.panel-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    letter-spacing: -0.02em;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary);
}}
.sticker-tag {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 8px;
    border: 2px solid var(--border-color);
    box-shadow: 2px 2px 0px var(--shadow-color);
    text-transform: uppercase;
    background: var(--accent-cyan);
    color: #111111;
    transform: rotate(1deg);
}}
.sticker-tag-pink {{
    background: var(--accent-pink);
    color: #FFFFFF;
    transform: rotate(-1.5deg);
}}
.sticker-tag-yellow {{
    background: var(--accent-yellow);
    color: #111111;
    transform: rotate(1.2deg);
}}

/* Streamlit Inputs & Textarea Overrides */
.stTextArea textarea {{
    background-color: var(--input-bg) !important;
    color: var(--text-primary) !important;
    border: 2.5px solid var(--border-color) !important;
    border-radius: 0px !important;
    box-shadow: 3px 3px 0px var(--shadow-color) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 12px 14px !important;
    line-height: 1.5 !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--accent-blue) !important;
    box-shadow: 4px 4px 0px var(--accent-blue) !important;
}}

/* Primary CTA Button (MAKE IT CHILL) */
.stButton > button[kind="primary"] {{
    background-color: var(--accent-yellow) !important;
    color: #111111 !important;
    border: 3px solid var(--border-color) !important;
    border-radius: 0px !important;
    box-shadow: 5px 5px 0px var(--shadow-color) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.02em !important;
    padding: 14px 24px !important;
    transition: all 0.12s ease-in-out !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translate(-2px, -2px) !important;
    box-shadow: 7px 7px 0px var(--shadow-color) !important;
    background-color: #FFF04D !important;
}}
.stButton > button[kind="primary"]:active {{
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px var(--shadow-color) !important;
}}

/* Secondary / Standard Buttons */
.stButton > button[kind="secondary"], .stButton > button:not([kind="primary"]) {{
    background-color: var(--bg-panel) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 0px !important;
    box-shadow: 3px 3px 0px var(--shadow-color) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    transition: all 0.12s ease !important;
}}
.stButton > button:not([kind="primary"]):hover {{
    transform: translate(-1px, -1px) !important;
    box-shadow: 4px 4px 0px var(--shadow-color) !important;
}}

/* Tone Selector Radio Styling */
[data-testid="stRadio"] > div {{
    gap: 12px !important;
}}
[data-testid="stRadio"] label {{
    background: var(--bg-panel) !important;
    border: 2px solid var(--border-color) !important;
    box-shadow: 2.5px 2.5px 0px var(--shadow-color) !important;
    padding: 8px 16px !important;
    border-radius: 0px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    color: var(--text-primary) !important;
}}

/* Analysis Metric Cards */
.analysis-metric-card {{
    background: var(--bg-panel);
    border: 2.5px solid var(--border-color);
    box-shadow: 4px 4px 0px var(--shadow-color);
    padding: 14px 16px;
    height: 100%;
}}
.metric-super-title {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}}
.metric-bold-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.2;
}}

/* Sentiment Comic Badges */
.badge-angry {{
    background: var(--accent-pink);
    color: #FFFFFF;
    padding: 3px 8px;
    border: 2px solid var(--border-color);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    display: inline-block;
}}
.badge-frustrated {{
    background: var(--accent-orange);
    color: #FFFFFF;
    padding: 3px 8px;
    border: 2px solid var(--border-color);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    display: inline-block;
}}
.badge-anxious {{
    background: var(--accent-yellow);
    color: #111111;
    padding: 3px 8px;
    border: 2px solid var(--border-color);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    display: inline-block;
}}
.badge-disappointed {{
    background: var(--accent-blue);
    color: #FFFFFF;
    padding: 3px 8px;
    border: 2px solid var(--border-color);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    display: inline-block;
}}
.badge-neutral {{
    background: var(--accent-cyan);
    color: #111111;
    padding: 3px 8px;
    border: 2px solid var(--border-color);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    display: inline-block;
}}

/* Quality Check Status Stamps */
.status-stamp {{
    display: inline-block;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 900;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 6px 14px;
    border: 3px solid var(--border-color);
    box-shadow: 3px 3px 0px var(--shadow-color);
    transform: rotate(-1deg);
}}
.stamp-compliant {{
    background: #4ADE80;
    color: #052E16;
}}
.stamp-partially {{
    background: var(--accent-yellow);
    color: #111111;
}}
.stamp-noncompliant {{
    background: var(--accent-pink);
    color: #FFFFFF;
}}

/* Centerpiece Final Word Box */
.final-word-container {{
    background: var(--bg-panel);
    border: 3.5px solid var(--border-color);
    box-shadow: 7px 7px 0px var(--shadow-color);
    padding: 26px 28px;
    margin: 24px 0;
    position: relative;
}}
.final-word-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2.5px solid var(--border-color);
    padding-bottom: 14px;
    margin-bottom: 18px;
}}
.final-word-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-primary);
}}
.final-speech-bubble {{
    background: var(--bg-panel-alt);
    border: 2.5px solid var(--border-color);
    padding: 22px 24px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--text-primary);
    white-space: pre-wrap;
    box-shadow: 4px 4px 0px var(--shadow-color);
    position: relative;
    border-radius: 0px;
}}

/* Original Draft Panel */
.original-draft-box {{
    background: var(--bg-panel);
    border: 2px solid var(--border-color);
    box-shadow: 3px 3px 0px var(--shadow-color);
    padding: 16px 20px;
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
}}

/* Tone Scores Visual Progress Meters */
.tone-score-card {{
    background: var(--bg-panel);
    border: 2px solid var(--border-color);
    box-shadow: 3px 3px 0px var(--shadow-color);
    padding: 10px 12px;
    text-align: center;
}}
.tone-score-val {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 900;
    color: var(--accent-blue);
}}
.tone-score-lbl {{
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--text-muted);
}}

/* Expander Overrides */
.streamlit-expanderHeader {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    border: 2px solid var(--border-color) !important;
    box-shadow: 2px 2px 0px var(--shadow-color) !important;
    border-radius: 0px !important;
    background: var(--bg-panel) !important;
}}
</style>
"""
    return css
