"""
ChillGPT — Customer Support Response Assistant
Part 2: Response Review and Policy Validation Module
Professional Enterprise Complaint Management & Response Assistant
Visual Identity: Clean Modern SaaS, Fluid Navigation, Refined Motion & Accessible Contrast
Author: Member 2 (Vedant)
"""

import os
import sys
from pathlib import Path
import streamlit as st
import json

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from modules.response_reviewer import review_response
from config import get_custom_css, APP_TITLE, APP_ICON

# Page Configuration
st.set_page_config(
    page_title=f"{APP_TITLE} | Quality & Policy Audit (Part 2)",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"

# Inject Dynamic CSS
st.markdown(get_custom_css(st.session_state["theme_mode"]), unsafe_allow_html=True)

# Preset Scenarios
PRESETS = {
    "Scenario 1: Unauthorized Instant Refund": {
        "complaint": "I received my coffee maker yesterday but the glass carafe is completely shattered! I demand a full refund immediately.",
        "policy": "Return & Refund Policy: Damaged items must be reported within 48 hours with photographic proof. Refunds are subject to warehouse inspection and are processed to the original payment method within 5-7 business days. Instant refunds are strictly prohibited.",
        "response": "Hello! I am so sorry about the broken carafe. Don't worry at all, I have processed an immediate full refund back to your card right now! Have a great day!"
    },
    "Scenario 2: Missing Order Details & Defect Proof": {
        "complaint": "The headphones I received sound completely distorted and one side doesn't work at all. Fix this!",
        "policy": "Defective electronics must be reported within 14 days of delivery. Customers must provide the Order ID and a short video or image demonstrating the defect. Upon verification, a prepaid return label and replacement will be issued.",
        "response": "Hi there, thank you for reaching out. We apologize for the trouble with the headphones. We will get this sorted out for you as soon as possible. Best regards, Support Team."
    },
    "Scenario 3: Unprofessional / Hostile Tone": {
        "complaint": "Where is my order? It has been 5 days and your tracking link hasn't updated at all! Terrible service.",
        "policy": "Standard shipping takes 3-5 business days. In-transit delivery inquiries require Order ID and postal code. Agents must maintain a calm, empathetic, and professional tone at all times.",
        "response": "Bro, chill out. Stop spamming us. Delivery takes 5 business days, you didn't even read the checkout page lol. Just wait for the mailman instead of complaining."
    },
    "Scenario 4: Unrealistic Delivery Guarantee": {
        "complaint": "My anniversary is in two days and I haven't received my gift order #77124 yet. Can you make sure it arrives tomorrow?",
        "policy": "Expedited delivery is handled by third-party logistics. Guaranteed next-day delivery is only available when overnight shipping was purchased at checkout. Support agents must never guarantee next-day arrival without carrier confirmation.",
        "response": "Hello! Happy early anniversary! I 100% guarantee that your order #77124 will arrive at your doorstep tomorrow morning without fail. Warm regards, ChillGPT Team."
    },
    "Scenario 5: Fully Compliant & Professional Response": {
        "complaint": "My order #4892 arrived with a broken zipper on the jacket. I would like an exchange please.",
        "policy": "Damaged garments reported within 7 days are eligible for a free exchange upon receipt of a photograph showing the defect and the original order number.",
        "response": "Hello! Thank you for contacting ChillGPT support. We sincerely apologize for the broken zipper on your jacket and understand how disappointing this is. Since you provided order #4892, could you kindly reply with a clear photograph of the damaged zipper? Once received and verified, we will immediately send you a prepaid return label and dispatch your replacement jacket. Warm regards, ChillGPT Support Team."
    }
}

# Sidebar - Settings & Preset Selection
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 16px;">
        <div style="font-size: 1.05rem; font-weight: 800; letter-spacing: -0.02em;">
            🛡️ AUDITOR SETTINGS
        </div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
            Part 2 Quality Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    api_key_env = os.environ.get("GEMINI_API_KEY", "").strip()
    user_api_key = st.text_input(
        "Gemini API Key (Optional)",
        value=api_key_env,
        type="password",
        help="Leave empty for Deterministic Local Validation Mode."
    )

    if user_api_key:
        st.caption("🟢 Gemini API Active")
    else:
        st.caption("⚡ Deterministic Local Engine")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📋 Load Pre-configured Test Scenario")
    selected_scenario = st.selectbox(
        "Choose test case:",
        options=list(PRESETS.keys()),
        index=0,
        label_visibility="collapsed"
    )

    st.divider()
    theme_label = "🌙 Switch to Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Switch to Light Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

# Top Navbar
st.markdown(f"""
<div class="app-navbar">
    <div class="nav-brand-group">
        <div class="brand-logo-icon">🛡️</div>
        <div>
            <div class="brand-name">{APP_TITLE}</div>
            <div class="brand-tagline">Quality & Compliance Audit Module (Part 2)</div>
        </div>
    </div>
    <div class="nav-status-group">
        <div class="system-status-indicator">
            <div class="status-dot"></div>
            <span>Auditor Active</span>
        </div>
        <div class="pro-card-badge">
            {st.session_state['theme_mode'].upper()} MODE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Stepper
has_audited = ("review_results" in st.session_state)
st.markdown(f"""
<div class="workflow-stepper">
    <div class="step-card active-step">
        <div class="step-badge">01</div>
        <div class="step-text">
            <span class="step-title">Grievance & Terms</span>
            <span class="step-desc">Intake & Policy</span>
        </div>
    </div>
    <div class="step-card active-step">
        <div class="step-badge">02</div>
        <div class="step-text">
            <span class="step-title">Draft Response</span>
            <span class="step-desc">Agent or AI Text</span>
        </div>
    </div>
    <div class="step-card {'active-step' if has_audited else ''}">
        <div class="step-badge">03</div>
        <div class="step-text">
            <span class="step-title">Policy & Tone Audit</span>
            <span class="step-desc">Validation & Score</span>
        </div>
    </div>
    <div class="step-card {'active-step' if has_audited else ''}">
        <div class="step-badge">04</div>
        <div class="step-text">
            <span class="step-title">Approved Resolution</span>
            <span class="step-desc">Verified Response</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

preset_data = PRESETS[selected_scenario]

# 3 Columns for Intake, Policy, and Draft Response
col1, col2, col3 = st.columns([1.1, 1.1, 1.2], gap="medium")

with col1:
    st.markdown("""
    <div class="pro-card-header" style="margin-bottom: 8px;">
        <div class="pro-card-title">
            <span>📩</span> Customer Complaint
        </div>
        <span class="pro-card-badge">01 Intake</span>
    </div>
    """, unsafe_allow_html=True)
    complaint_input = st.text_area(
        "Complaint Input",
        value=preset_data["complaint"],
        height=180,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div class="pro-card-header" style="margin-bottom: 8px;">
        <div class="pro-card-title">
            <span>📋</span> Company Policy
        </div>
        <span class="pro-card-badge">02 Rules</span>
    </div>
    """, unsafe_allow_html=True)
    policy_input = st.text_area(
        "Policy Input",
        value=preset_data["policy"],
        height=180,
        label_visibility="collapsed"
    )

with col3:
    st.markdown("""
    <div class="pro-card-header" style="margin-bottom: 8px;">
        <div class="pro-card-title">
            <span>✍️</span> Response Draft to Audit
        </div>
        <span class="pro-card-badge">03 Draft</span>
    </div>
    """, unsafe_allow_html=True)
    response_input = st.text_area(
        "Draft Input",
        value=preset_data["response"],
        height=180,
        label_visibility="collapsed"
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
review_clicked = st.button("AUDIT & VALIDATE RESPONSE →", type="primary", use_container_width=True)

if review_clicked or "review_results" in st.session_state:
    if review_clicked:
        with st.spinner("Running Quality Audit against policy rules and tone guidelines..."):
            results = review_response(
                customer_complaint=complaint_input,
                company_policy=policy_input,
                generated_response=response_input,
                api_key=user_api_key if user_api_key else None
            )
            st.session_state["review_results"] = results
    else:
        results = st.session_state["review_results"]

    st.markdown("<hr style='border: 1px solid var(--border-color); margin: 36px 0 24px 0;'>", unsafe_allow_html=True)

    status = results.get("compliance_status", "Non-Compliant")
    chip_class = "chip-compliant" if status == "Compliant" else ("chip-partially" if status == "Partially Compliant" else "chip-noncompliant")
    mode = results.get("analysis_mode", "deterministic_fallback")
    mode_label = "🤖 Gemini AI Evaluation" if mode == "ai_gemini" else "⚙️ Deterministic Validation Engine"

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em;">
                🛡️ Audit Results & Compliance Assessment
            </div>
            <div class="status-chip {chip_class}">
                {status}
            </div>
        </div>
        <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:var(--text-muted);">{mode_label}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2-Column Audit Breakdown
    res_col1, res_col2 = st.columns(2, gap="medium")
    with res_col1:
        st.markdown("""
        <div class="metric-tile">
            <div class="metric-tile-label" style="margin-bottom: 8px;">⚖️ Policy Violations & Commitments</div>
        """, unsafe_allow_html=True)
        violations = results.get("policy_violations", [])
        if violations:
            for v in violations:
                st.markdown(f"""
                <div class="alert-container-danger">
                    <strong>Policy Violation:</strong> {v}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-container-success">
                ✅ <strong>No policy violations detected:</strong> The draft strictly adheres to company guidelines.
            </div>
            """, unsafe_allow_html=True)

        fp_data = results.get("false_promises", {})
        fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"
        if fp_detected:
            for s in fp_data.get("suspicious_statements", []):
                st.markdown(f"""
                <div class="alert-container-warning">
                    ⚠️ <strong>False Promise Alert:</strong> <em>"{s}"</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-container-success">
                ✅ <strong>Zero false promises:</strong> No unauthorized commitments made to the customer.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with res_col2:
        st.markdown("""
        <div class="metric-tile">
            <div class="metric-tile-label" style="margin-bottom: 8px;">📋 Required Customer Details</div>
        """, unsafe_allow_html=True)
        missing = results.get("missing_information", [])
        if missing:
            for idx, item in enumerate(missing, 1):
                st.markdown(f"""
                <div class="alert-container-warning">
                    <strong>{idx}. {item.get('item', 'Item')}:</strong> {item.get('reason', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-container-success">
                ✅ <strong>Complete:</strong> All necessary verification details requested from the customer.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Tone Scores (1-10)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    scores = results.get("tone_scores", {})
    sc_cols = st.columns(5)
    metrics_meta = [
        ("Professionalism", scores.get("professionalism", 7)),
        ("Empathy", scores.get("empathy", 5)),
        ("Politeness", scores.get("politeness", 6)),
        ("Clarity", scores.get("clarity", 7)),
        ("Friendliness", scores.get("customer_friendliness", 6)),
    ]
    for col, (label, val) in zip(sc_cols, metrics_meta):
        with col:
            st.markdown(f"""
            <div class="tone-metric-row">
                <div class="tone-score-num">{val}/10</div>
                <div class="tone-score-tag">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(max(0.0, min(1.0, val / 10.0)))

    # Final Word Centerpiece
    st.markdown("<hr style='border: 1px solid var(--border-color); margin: 34px 0 20px 0;'>", unsafe_allow_html=True)
    improved_text = results.get("improved_response", "")

    st.markdown(f"""
    <div class="resolution-card">
        <div class="resolution-header">
            <div style="font-size: 1.15rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                <span>✨</span> Final Audited Response
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="status-chip chip-compliant">AUDITED</span>
            </div>
        </div>
        <div class="resolution-body">
{improved_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 📄 Markdown Code Copy")
    st.code(improved_text, language="markdown")

# Footer
st.markdown(f"""
<div class="pro-footer">
    <div class="pro-footer-brand">
        <span>🛡️</span> {APP_TITLE} · Response Review & Policy Validation Module (Part 2)
    </div>
    <div class="pro-footer-meta">
        Author: Member 2 (Vedant) · 2026 Enterprise Edition
    </div>
</div>
""", unsafe_allow_html=True)
