"""
ChillGPT — Quality & Policy Audit Module
Part 2: Response Review and Policy Validation Module
Visual Identity: Minimalist Creative Portfolio + Cute AI Mascot "Chilly"
Author: Member 2 (Vedant)
"""

import os
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import json

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from modules.response_reviewer import review_response
from config import get_custom_css, render_mascot_component, APP_TITLE, APP_ICON

# Page Configuration
st.set_page_config(
    page_title=f"{APP_TITLE} ✦ Quality & Policy Audit (Part 2)",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
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
    <div style="padding: 10px 0 12px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 16px;">
        <div style="font-size: 1.1rem; font-weight: 800; letter-spacing: -0.02em;">
            🛡️ AUDITOR SETTINGS
        </div>
        <div style="font-size: 0.76rem; color: var(--text-muted); text-transform: uppercase;">
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
    theme_label = "🌙 Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Light Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

# Top Navbar
nav_c1, nav_spacer, nav_theme = st.columns([3, 4, 1.2], gap="small")
with nav_c1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; padding-top:4px;">
        <span style="font-size:1.25rem;">✨</span>
        <span style="font-weight:800; font-size:1.15rem; letter-spacing:-0.03em;">{APP_TITLE}</span>
        <span class="portfolio-pill-badge">PART 2 AUDITOR</span>
    </div>
    """, unsafe_allow_html=True)

with nav_theme:
    mode_icon = "🌙" if st.session_state["theme_mode"] == "light" else "☀️"
    mode_txt = "Dark" if st.session_state["theme_mode"] == "light" else "Light"
    if st.button(f"{mode_icon} {mode_txt}", use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

has_audited = ("review_results" in st.session_state)
mascot_state = "success" if has_audited else "idle"
mascot_msg = "Audit complete! Here are the compliance checks ✦" if has_audited else "Ready to verify the response against policy rules."

# Central Animated Mascot Component
components.html(render_mascot_component(
    state=mascot_state,
    message=mascot_msg,
    theme=st.session_state["theme_mode"]
), height=210)

preset_data = PRESETS[selected_scenario]

# 2-Column Compact Intake
col_inputs, col_draft = st.columns([1.1, 1.1], gap="large")

with col_inputs:
    st.markdown("""
    <div style="font-weight:700; font-size:0.95rem; margin-bottom:6px;">
        📩 Customer Grievance & Policy
    </div>
    """, unsafe_allow_html=True)
    complaint_input = st.text_area(
        "Complaint Input",
        value=preset_data["complaint"],
        height=100,
        label_visibility="collapsed",
        placeholder="Customer complaint text..."
    )
    policy_input = st.text_area(
        "Policy Input",
        value=preset_data["policy"],
        height=100,
        label_visibility="collapsed",
        placeholder="Company policy rules..."
    )

with col_draft:
    st.markdown("""
    <div style="font-weight:700; font-size:0.95rem; margin-bottom:6px;">
        ✍️ Draft Response to Audit
    </div>
    """, unsafe_allow_html=True)
    response_input = st.text_area(
        "Draft Input",
        value=preset_data["response"],
        height=145,
        label_visibility="collapsed"
    )

    review_clicked = st.button("AUDIT & VALIDATE RESPONSE ✦", type="primary", use_container_width=True)

if review_clicked or "review_results" in st.session_state:
    if review_clicked:
        with st.spinner("✨ Running Quality Audit against policy rules and tone guidelines..."):
            results = review_response(
                customer_complaint=complaint_input,
                company_policy=policy_input,
                generated_response=response_input,
                api_key=user_api_key if user_api_key else None
            )
            st.session_state["review_results"] = results
    else:
        results = st.session_state["review_results"]

    status = results.get("compliance_status", "Non-Compliant")
    chip_class = "chip-compliant" if status == "Compliant" else ("chip-partially" if status == "Partially Compliant" else "chip-noncompliant")
    mode = results.get("analysis_mode", "deterministic_fallback")
    mode_label = "🤖 Gemini AI Evaluation" if mode == "ai_gemini" else "⚙️ Deterministic Validation Engine"
    improved_text = results.get("improved_response", "")

    st.markdown("<hr style='border: 1px solid var(--border-color); margin: 28px 0 20px 0;'>", unsafe_allow_html=True)

    # FINAL AUDITED RESPONSE READING CANVAS
    st.markdown(f"""
    <div class="reading-canvas">
        <div class="reading-canvas-header">
            <div class="reading-canvas-title">
                <span>✨</span> Final Audited Response
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="status-chip {chip_class}">{status}</span>
                <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:var(--text-muted);">{mode_label}</span>
            </div>
        </div>
        <div class="reading-canvas-body">
{improved_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1-Click Copy Button
    copy_html = f"""
    <button id="copyFinalBtn" onclick="copyFinalResponse()" style="
        background: #262422;
        color: #FFFFFF;
        border: none;
        border-radius: 999px;
        padding: 12px 26px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        margin-bottom: 16px;
    ">
        <span id="copyIcon">📋</span> <span id="copyText">Copy Audited Response</span>
    </button>
    <script>
    function copyFinalResponse() {{
        const text = {json.dumps(improved_text)};
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('copyFinalBtn');
            const icon = document.getElementById('copyIcon');
            const label = document.getElementById('copyText');
            btn.style.background = '#059669';
            icon.innerText = '✅';
            label.innerText = 'Copied to Clipboard!';
            setTimeout(() => {{
                btn.style.background = '#262422';
                icon.innerText = '📋';
                label.innerText = 'Copy Audited Response';
            }}, 2500);
        }}).catch(err => console.error(err));
    }}
    </script>
    """
    components.html(copy_html, height=54)

    # Tabs for Audit Details
    tab_customer_tone, tab_audit_details, tab_tone, tab_raw_json = st.tabs([
        "🔍 Customer Tone & Emotion Analysis",
        "🛡️ Policy & Information Verification",
        "📊 5-Dimension Tone Scores",
        "🛠️ Raw Audit JSON"
    ])

    with tab_customer_tone:
        complaint_lower = complaint_input.lower()
        if any(w in complaint_lower for w in ["furious", "unacceptable", "scam", "shattered", "ridiculous", "terrible", "lawyer"]):
            c_sentiment = "Angry / Hostile"
            c_intensity = "9/10"
            c_badge = "badge-frustrated"
            c_urgency = "High Escalation Risk"
        elif any(w in complaint_lower for w in ["distorted", "broken", "fix this", "annoyed", "waiting", "failed"]):
            c_sentiment = "Frustrated / Agitated"
            c_intensity = "8/10"
            c_badge = "badge-frustrated"
            c_urgency = "Elevated Friction"
        elif any(w in complaint_lower for w in ["anniversary", "birthday", "gift", "tomorrow", "urgent"]):
            c_sentiment = "Anxious / Urgent"
            c_intensity = "7/10"
            c_badge = "badge-anxious"
            c_urgency = "Time-Sensitive"
        else:
            c_sentiment = "Neutral / Direct"
            c_intensity = "5/10"
            c_badge = "badge-neutral"
            c_urgency = "Standard Inquiry"

        st.markdown(f"""
        <div style="background: var(--bg-card-alt); border: 1px solid var(--border-color); border-radius: 18px; padding: 20px 24px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <span class="emotion-badge {c_badge}">CUSTOMER TONE: {c_sentiment.upper()}</span>
                <span class="portfolio-pill-badge">{c_urgency}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 10px;">
                <div class="metric-tile">
                    <div class="metric-tile-label">Customer Emotion</div>
                    <div class="metric-tile-value">💬 {c_sentiment}</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">Emotional Intensity</div>
                    <div class="metric-tile-value">⚡ {c_intensity}</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">Urgency Level</div>
                    <div class="metric-tile-value">⏱️ {c_urgency}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_audit_details:
        res_col1, res_col2 = st.columns(2, gap="medium")
        with res_col1:
            st.markdown("**Policy Violations & False Promises**")
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
                    ✅ <strong>No policy violations detected:</strong> The draft strictly adheres to company rules.
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
                    ✅ <strong>Zero false promises:</strong> No unauthorized commitments made.
                </div>
                """, unsafe_allow_html=True)

        with res_col2:
            st.markdown("**Required Customer Details**")
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
                    ✅ <strong>Complete:</strong> All necessary verification details requested.
                </div>
                """, unsafe_allow_html=True)

    with tab_tone:
        scores = results.get("tone_scores", {})
        sc_cols = st.columns(5)
        metrics_meta = [
            ("Professional", scores.get("professionalism", 7)),
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

    with tab_raw_json:
        st.json(results)

# Footer
st.markdown(f"""
<div class="portfolio-footer">
    <div class="portfolio-footer-brand">
        <span>✨</span> {APP_TITLE} · Response Review & Policy Validation Module (Part 2)
    </div>
    <div>
        Author: Member 2 (Vedant) · 2026
    </div>
</div>
""", unsafe_allow_html=True)
