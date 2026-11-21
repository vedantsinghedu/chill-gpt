"""
ChillGPT - Application Configuration and UI Themes
Professional Enterprise Complaint Management & Response Assistant
Visual Identity: Clean Modern SaaS, Fluid Navigation, Refined Motion & Accessible Contrast
"""

import json
from pathlib import Path
from typing import List, Dict, Any

APP_TITLE = "ChillGPT"
APP_SUBTITLE = "AI Customer Support Response Assistant"
APP_TAGLINE = "Empathetic, policy-compliant customer complaint resolution"
APP_ICON = "🛡️"

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
    Generates a professional, responsive enterprise stylesheet with:
    - Fluid navigation & tab styling
    - Motion-safe subtle transitions and micro-interactions
    - Accessible, high-contrast light and dark modes
    - Clear visual hierarchy for complaint workflows
    """
    is_dark = (theme == "dark")

    if is_dark:
        bg_main = "#0B0F17"
        bg_card = "#141C2B"
        bg_card_alt = "#1B2436"
        bg_sidebar = "#0E1522"
        text_primary = "#F8FAFC"
        text_secondary = "#CBD5E1"
        text_muted = "#94A3B8"
        border_color = "rgba(255, 255, 255, 0.10)"
        border_strong = "rgba(255, 255, 255, 0.20)"
        primary_blue = "#3B82F6"
        primary_blue_hover = "#60A5FA"
        primary_blue_light = "rgba(59, 130, 246, 0.15)"
        accent_teal = "#14B8A6"
        status_compliant_bg = "#064E3B"
        status_compliant_text = "#6EE7B7"
        status_compliant_border = "#059669"
        status_warning_bg = "#451A03"
        status_warning_text = "#FCD34D"
        status_warning_border = "#B45309"
        status_danger_bg = "#4C0519"
        status_danger_text = "#FDA4AF"
        status_danger_border = "#BE123C"
        input_bg = "#111827"
        shadow_card = "0 4px 16px rgba(0, 0, 0, 0.35)"
        shadow_float = "0 10px 30px rgba(0, 0, 0, 0.45)"
    else:
        bg_main = "#F8FAFC"
        bg_card = "#FFFFFF"
        bg_card_alt = "#F1F5F9"
        bg_sidebar = "#FFFFFF"
        text_primary = "#0F172A"
        text_secondary = "#334155"
        text_muted = "#64748B"
        border_color = "#E2E8F0"
        border_strong = "#CBD5E1"
        primary_blue = "#1D4ED8"
        primary_blue_hover = "#1E40AF"
        primary_blue_light = "#EFF6FF"
        accent_teal = "#0D9488"
        status_compliant_bg = "#ECFDF5"
        status_compliant_text = "#065F46"
        status_compliant_border = "#A7F3D0"
        status_warning_bg = "#FFFBEB"
        status_warning_text = "#92400E"
        status_warning_border = "#FDE68A"
        status_danger_bg = "#FEF2F2"
        status_danger_text = "#991B1B"
        status_danger_border = "#FECACA"
        input_bg = "#FFFFFF"
        shadow_card = "0 2px 8px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02)"
        shadow_float = "0 12px 28px -4px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.03)"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

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
    --primary-blue: {primary_blue};
    --primary-blue-hover: {primary_blue_hover};
    --primary-blue-light: {primary_blue_light};
    --accent-teal: {accent_teal};
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
    --shadow-card: {shadow_card};
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
        transform: translateY(6px);
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
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

/* Streamlit Block Container spacing */
.main .block-container {{
    max-width: 1240px;
    padding-top: 1.5rem;
    padding-bottom: 3.5rem;
}}

/* Sidebar Overrides */
[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: var(--text-primary) !important;
    margin-top: 0 !important;
}}

/* Header Navigation Bar */
.app-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 18px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    box-shadow: var(--shadow-card);
    margin-bottom: 24px;
    transition: all 0.2s ease;
}}
.nav-brand-group {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.brand-logo-icon {{
    background: var(--primary-blue);
    color: #FFFFFF;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
}}
.brand-name {{
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1.1;
}}
.brand-tagline {{
    font-size: 0.76rem;
    color: var(--text-muted);
    font-weight: 500;
}}

.nav-status-group {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.system-status-indicator {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-secondary);
    background: var(--bg-card-alt);
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid var(--border-color);
}}
.status-dot {{
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}}

/* Workflow Stepper / Pipeline Header */
.workflow-stepper {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 26px;
}}
.step-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: var(--shadow-card);
    transition: transform 0.15s ease, border-color 0.15s ease;
}}
.step-card:hover {{
    border-color: var(--primary-blue);
    transform: translateY(-1px);
}}
.step-badge {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: var(--bg-card-alt);
    color: var(--text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
}}
.step-card.active-step {{
    border-color: var(--primary-blue);
    background: var(--primary-blue-light);
}}
.step-card.active-step .step-badge {{
    background: var(--primary-blue);
    color: #FFFFFF;
}}
.step-text {{
    display: flex;
    flex-direction: column;
}}
.step-title {{
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}}
.step-desc {{
    font-size: 0.72rem;
    color: var(--text-muted);
}}

/* Card Surfaces */
.pro-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: var(--shadow-card);
    margin-bottom: 20px;
    transition: all 0.15s ease;
    animation: fadeInScale 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}}
.pro-card:hover {{
    box-shadow: var(--shadow-float);
}}
.pro-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 14px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
}}
.pro-card-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.015em;
}}
.pro-card-badge {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 4px 10px;
    border-radius: 6px;
    background: var(--bg-card-alt);
    color: var(--text-muted);
    border: 1px solid var(--border-color);
}}

/* Form Inputs (Text Area) */
.stTextArea textarea {{
    background-color: var(--input-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.94rem !important;
    line-height: 1.6 !important;
    padding: 12px 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--primary-blue) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}}

/* Interactive Buttons */
.stButton > button[kind="primary"] {{
    background-color: var(--primary-blue) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: var(--primary-blue-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
}}
.stButton > button[kind="primary"]:active {{
    transform: translateY(1px) !important;
}}

.stButton > button:not([kind="primary"]) {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 18px !important;
    transition: all 0.15s ease !important;
}}
.stButton > button:not([kind="primary"]):hover {{
    background-color: var(--bg-card-alt) !important;
    border-color: var(--primary-blue) !important;
}}

/* Segmented Tone Selector */
[data-testid="stRadio"] > div {{
    gap: 8px !important;
}}
[data-testid="stRadio"] label {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: var(--text-secondary) !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: var(--primary-blue) !important;
    color: var(--primary-blue) !important;
}}

/* Metrics Grid */
.metric-tile {{
    background: var(--bg-card-alt);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 14px 16px;
    height: 100%;
    transition: transform 0.15s ease;
}}
.metric-tile:hover {{
    transform: translateY(-1px);
}}
.metric-tile-label {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 4px;
}}
.metric-tile-value {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* Status Indicator Badges */
.status-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
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
    border-left: 4px solid #DC2626;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    color: var(--status-danger-text);
    margin-bottom: 10px;
}}
.alert-container-warning {{
    background: var(--status-warning-bg);
    border-left: 4px solid #D97706;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    color: var(--status-warning-text);
    margin-bottom: 10px;
}}
.alert-container-success {{
    background: var(--status-compliant-bg);
    border-left: 4px solid #10B981;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    color: var(--status-compliant-text);
    margin-bottom: 10px;
}}

/* Tone Scores Visual Progress Meters */
.tone-metric-row {{
    background: var(--bg-card-alt);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
}}
.tone-score-num {{
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--primary-blue);
    font-family: 'JetBrains Mono', monospace;
}}
.tone-score-tag {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 2px;
}}

/* Resolution Centerpiece Card */
.resolution-card {{
    background: var(--bg-card);
    border: 1.5px solid var(--border-strong);
    border-radius: 16px;
    padding: 26px 28px;
    box-shadow: var(--shadow-float);
    margin: 24px 0;
    animation: fadeInScale 0.25s ease;
}}
.resolution-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 16px;
    margin-bottom: 20px;
}}
.resolution-body {{
    background: var(--bg-card-alt);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 22px 24px;
    font-size: 1.02rem;
    line-height: 1.7;
    color: var(--text-primary);
    white-space: pre-wrap;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* Tabs Styling */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 8px !important;
    background: var(--bg-card) !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: var(--text-muted) !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background: var(--primary-blue) !important;
    color: #FFFFFF !important;
}}

/* Expanders */
.streamlit-expanderHeader {{
    border-radius: 10px !important;
    border: 1px solid var(--border-color) !important;
    background: var(--bg-card) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: all 0.15s ease !important;
}}
.streamlit-expanderHeader:hover {{
    background: var(--bg-card-alt) !important;
}}

/* Professional Footer */
.pro-footer {{
    border-top: 1px solid var(--border-color);
    padding: 24px 0 12px 0;
    margin-top: 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: var(--text-muted);
    flex-wrap: wrap;
    gap: 12px;
}}
.pro-footer-brand {{
    font-weight: 700;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
}}
.pro-footer-meta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: var(--text-muted);
}}
</style>
"""
    return css
