"""
ChillGPT - Application Configuration and UI Themes
Visual Identity: Neo-Minimalist Editorial & Pop Yellow Design
Inspired by Wave AI / Rabbit r1 / Modern Japanese & Swiss Studio Aesthetic
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
    Generates dynamic CSS for the sleek, editorial Swiss/Japanese pop-yellow design.
    Matches the WaveAI aesthetic from new-design.mp4:
    - Giant ultra-bold condensed typography
    - Pop canary yellow (#FFC700 / #FFBE00) hero container with cute mascot & phone frame
    - Minimalist numbered editorial cards (01, 02, 03) with rounded corners (24px)
    - Ticker marquee line
    - Deep black pill buttons and brackets navigation [ PRODUCT ]
    """
    is_dark = (theme == "dark")

    if is_dark:
        bg_main = "#0D0D11"
        bg_card = "#16181F"
        bg_card_alt = "#1E202A"
        bg_sidebar = "#111217"
        text_primary = "#FFFFFF"
        text_secondary = "#B0B3BD"
        text_muted = "#727788"
        border_subtle = "rgba(255, 255, 255, 0.12)"
        border_solid = "#FFFFFF"
        pop_yellow = "#FFCC00"
        btn_bg = "#FFFFFF"
        btn_text = "#000000"
        phone_bezel = "#222530"
        phone_screen = "#FFCC00"
        phone_screen_text = "#000000"
    else:
        bg_main = "#FFFFFF"
        bg_card = "#F4F4F6"
        bg_card_alt = "#EAEAEF"
        bg_sidebar = "#F8F8FA"
        text_primary = "#000000"
        text_secondary = "#444444"
        text_muted = "#777777"
        border_subtle = "rgba(0, 0, 0, 0.08)"
        border_solid = "#000000"
        pop_yellow = "#FFC700"
        btn_bg = "#000000"
        btn_text = "#FFFFFF"
        phone_bezel = "#0A0A0A"
        phone_screen = "#FFC700"
        phone_screen_text = "#000000"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Anton&display=swap');

:root {{
    --bg-main: {bg_main};
    --bg-card: {bg_card};
    --bg-card-alt: {bg_card_alt};
    --bg-sidebar: {bg_sidebar};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-muted: {text_muted};
    --border-subtle: {border_subtle};
    --border-solid: {border_solid};
    --pop-yellow: {pop_yellow};
    --btn-bg: {btn_bg};
    --btn-text: {btn_text};
    --phone-bezel: {phone_bezel};
    --phone-screen: {phone_screen};
    --phone-screen-text: {phone_screen_text};
}}

/* Main Canvas */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}}

[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle) !important;
}}

/* Clean typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: var(--text-primary) !important;
}}

/* Header Navigation Bar (Matches frame 00:00) */
.site-nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 0 16px 0;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border-subtle);
    font-family: 'Space Mono', monospace;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.nav-brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 900;
    font-size: 1.15rem;
    letter-spacing: -0.03em;
    color: var(--text-primary);
}}
.nav-links {{
    display: flex;
    gap: 20px;
    color: var(--text-muted);
}}
.nav-link-item {{
    cursor: default;
    transition: color 0.15s ease;
}}
.nav-link-item:hover {{
    color: var(--text-primary);
}}
.nav-pill-badge {{
    background: #000000;
    color: #FFFFFF;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}}

/* GIANT BACKGROUND TYPOGRAPHY (Matches frame 00:00 FORECASTS) */
.giant-bg-word {{
    font-family: 'Anton', 'Space Grotesk', sans-serif;
    font-size: clamp(3.8rem, 11vw, 9.5rem);
    font-weight: 900;
    line-height: 0.88;
    letter-spacing: -0.04em;
    text-transform: uppercase;
    color: var(--text-primary);
    text-align: center;
    margin: 10px 0 -45px 0;
    user-select: none;
    z-index: 1;
    position: relative;
}}

/* HERO POP-YELLOW CONTAINER (Matches frame 00:00 - 00:02) */
.hero-yellow-container {{
    background-color: var(--pop-yellow);
    border-radius: 28px;
    padding: 34px 38px;
    margin: 0 0 32px 0;
    color: #000000;
    position: relative;
    z-index: 2;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.06);
}}
.hero-content-grid {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
}}
.hero-left-desc {{
    flex: 1;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    line-height: 1.5;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #111111;
    max-width: 320px;
}}
.hero-pill-btn {{
    background: #000000;
    color: #FFFFFF;
    border-radius: 999px;
    padding: 10px 22px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 0.88rem;
    border: none;
    cursor: pointer;
    display: inline-block;
    margin-top: 14px;
    transition: transform 0.15s ease, background-color 0.15s ease;
}}
.hero-pill-btn:hover {{
    transform: scale(1.04);
    background-color: #222222;
}}

/* PHONE MOCKUP IN CENTER (Matches frame 00:00 & 00:08) */
.phone-mockup-wrap {{
    display: flex;
    justify-content: center;
    align-items: center;
}}
.phone-device {{
    background: var(--phone-bezel);
    border-radius: 40px;
    padding: 9px;
    box-shadow: 0 20px 48px rgba(0, 0, 0, 0.22);
    width: 200px;
    height: 290px;
    position: relative;
    display: flex;
    flex-direction: column;
}}
.phone-notch {{
    width: 65px;
    height: 14px;
    background: #000000;
    border-radius: 20px;
    margin: 3px auto 6px auto;
    z-index: 5;
}}
.phone-inner-screen {{
    background-color: var(--phone-screen);
    border-radius: 32px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: var(--phone-screen-text);
    padding: 14px;
    position: relative;
    overflow: hidden;
}}
.phone-mascot-face {{
    font-size: 4.8rem;
    line-height: 1;
    margin-bottom: 4px;
    filter: drop-shadow(0 6px 12px rgba(0,0,0,0.18));
}}
.phone-app-pill {{
    background: #000000;
    color: #FFFFFF;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    margin-top: 6px;
    letter-spacing: 0.05em;
}}

.hero-right-meta {{
    flex: 1;
    text-align: right;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    line-height: 1.6;
    text-transform: uppercase;
    color: #222222;
    max-width: 320px;
}}

/* TICKER MARQUEE (Matches frame 00:03 - 00:06) */
.ticker-wrap {{
    width: 100%;
    overflow: hidden;
    padding: 10px 0;
    border-top: 1px solid var(--border-subtle);
    border-bottom: 1px solid var(--border-subtle);
    margin: 0 0 32px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
}}

/* NUMBERED EDITORIAL CARDS (Matches frame 00:13 - 00:15: 01, 02, 03) */
.editorial-card {{
    background-color: var(--bg-card);
    border-radius: 24px;
    padding: 26px 28px;
    height: 100%;
    border: 1px solid var(--border-subtle);
    transition: transform 0.15s ease, background-color 0.15s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.editorial-card:hover {{
    background-color: var(--bg-card-alt);
}}
.card-big-num {{
    font-family: 'Anton', 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    line-height: 1;
    color: var(--text-primary);
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}}
.card-header-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    margin-bottom: 6px;
}}
.card-sub-desc {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 14px;
}}

/* TEXTAREA STYLING */
.stTextArea textarea {{
    background-color: #FFFFFF !important;
    color: #111111 !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    border-radius: 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 14px 16px !important;
    line-height: 1.55 !important;
    box-shadow: none !important;
}}
.stTextArea textarea:focus {{
    border-color: #000000 !important;
    box-shadow: 0 0 0 2px rgba(0,0,0,0.1) !important;
}}

/* CTA PRIMARY BUTTON */
.stButton > button[kind="primary"] {{
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 999px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
    padding: 14px 32px !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
    text-transform: uppercase !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    background-color: #222222 !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22) !important;
}}

/* SECONDARY BUTTONS */
.stButton > button:not([kind="primary"]) {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 999px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 10px 20px !important;
    transition: all 0.12s ease !important;
}}
.stButton > button:not([kind="primary"]):hover {{
    background-color: var(--bg-card-alt) !important;
}}

/* TONE SELECTOR CAPSULE */
[data-testid="stRadio"] > div {{
    gap: 10px !important;
}}
[data-testid="stRadio"] label {{
    background: #FFFFFF !important;
    border: 1px solid var(--border-subtle) !important;
    padding: 8px 18px !important;
    border-radius: 999px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    cursor: pointer !important;
    color: #111111 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
}}

/* OUTPUT METRICS CAPSULES */
.metric-capsule {{
    background: var(--bg-card);
    border-radius: 20px;
    padding: 18px 20px;
    border: 1px solid var(--border-subtle);
}}
.metric-capsule-lbl {{
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}}
.metric-capsule-val {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text-primary);
}}

/* STATUS PILL BADGES */
.status-pill {{
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
.status-compliant {{
    background: #000000;
    color: #4ADE80;
}}
.status-partially {{
    background: #FFC700;
    color: #000000;
}}
.status-noncompliant {{
    background: #EF4444;
    color: #FFFFFF;
}}

/* FINAL WORD SHOWCASE (Matches frame 00:08 - 00:10 Phone App UI) */
.showcase-container {{
    background-color: var(--bg-card);
    border-radius: 32px;
    padding: 32px 36px;
    border: 1px solid var(--border-subtle);
    margin: 28px 0;
}}
.showcase-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 16px;
    margin-bottom: 20px;
}}
.showcase-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.showcase-bubble {{
    background: #FFFFFF;
    border-radius: 20px;
    padding: 24px 28px;
    border: 1px solid var(--border-subtle);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #111111;
    white-space: pre-wrap;
    box-shadow: 0 4px 14px rgba(0,0,0,0.03);
}}

/* BOTTOM GIANT WORDMARK (Matches frame 00:16 WAVEAI) */
.footer-giant-wordmark {{
    font-family: 'Anton', 'Space Grotesk', sans-serif;
    font-size: clamp(4rem, 13vw, 11rem);
    font-weight: 900;
    line-height: 0.85;
    letter-spacing: -0.04em;
    text-transform: uppercase;
    color: var(--text-primary);
    text-align: center;
    margin: 60px 0 20px 0;
    user-select: none;
}}
.footer-meta-line {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid var(--border-subtle);
    padding: 16px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
</style>
"""
    return css
