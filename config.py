"""
ChillGPT - Application Configuration and UI Themes
Contains app constants, sample data loaders, and custom styling.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

APP_TITLE = "ChillGPT"
APP_SUBTITLE = "Customer Support Response Assistant"
MODULE_TITLE = "Part 1: Complaint Analysis & Response Generation"
APP_ICON = "❄️"

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


# Custom CSS for a clean, modern, professional college demo UI
CUSTOM_CSS = """
<style>
/* Main Container Styling */
.main-header {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    padding: 24px;
    border-radius: 14px;
    color: #FFFFFF;
    margin-bottom: 24px;
    border: 1px solid #334155;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    color: #38BDF8;
    letter-spacing: -0.5px;
}
.main-header p {
    font-size: 1.05rem;
    color: #94A3B8;
    margin: 6px 0 0 0;
}
.badge-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-right: 8px;
}
.badge-part1 {
    background-color: #0284C7;
    color: #FFFFFF;
}
.badge-project {
    background-color: #334155;
    color: #E2E8F0;
}

/* Card Styling */
.metric-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    height: 100%;
}
.metric-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A;
}

/* Sentiment tags */
.sentiment-angry {
    color: #DC2626;
    background: #FEE2E2;
    padding: 4px 12px;
    border-radius: 16px;
    font-weight: 600;
    display: inline-block;
}
.sentiment-frustrated {
    color: #EA580C;
    background: #FFEDD5;
    padding: 4px 12px;
    border-radius: 16px;
    font-weight: 600;
    display: inline-block;
}
.sentiment-anxious {
    color: #D97706;
    background: #FEF3C7;
    padding: 4px 12px;
    border-radius: 16px;
    font-weight: 600;
    display: inline-block;
}
.sentiment-disappointed {
    color: #4F46E5;
    background: #EEF2FF;
    padding: 4px 12px;
    border-radius: 16px;
    font-weight: 600;
    display: inline-block;
}
.sentiment-neutral {
    color: #059669;
    background: #D1FAE5;
    padding: 4px 12px;
    border-radius: 16px;
    font-weight: 600;
    display: inline-block;
}

/* Response Box */
.response-container {
    background: #F8FAFC;
    border-left: 4px solid #0284C7;
    border-radius: 0 10px 10px 0;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #1E293B;
    border-top: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
    white-space: pre-wrap;
    font-size: 1rem;
}

/* Handoff card */
.handoff-box {
    background: #F0FDF4;
    border: 1px dashed #16A34A;
    border-radius: 10px;
    padding: 16px;
    margin-top: 16px;
}
.handoff-title {
    color: #15803D;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 6px;
}
</style>
"""
