"""
ChillGPT — Customer Support Response Assistant
Part 2: Response Review and Policy Validation Module
Visual Identity: Comic-Book Pop Art × Editorial Collage × Gen-Z Creative Studio
Author: Member 2 (Vedant)
"""

import os
import sys
from pathlib import Path
import streamlit as st
import json

# Add current directory and parent directory to sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from modules.response_reviewer import review_response
from config import get_custom_css

# Page Configuration
st.set_page_config(
    page_title="CHILLGPT ✦ QUALITY CHECK (PART 2)",
    page_icon="⚡",
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
    <div style="padding: 8px 0 14px 0; border-bottom: 2px solid var(--border-color); margin-bottom: 14px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 900;">
            ⚡ REVIEWER CONTROLS
        </div>
        <div style="font-family: 'Space Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">
            Part 2 Policy Engine
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
        st.markdown("<span class='sticker-tag sticker-tag-cyan'>🟢 Gemini API Active</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='sticker-tag sticker-tag-yellow'>⚡ Deterministic Local Engine</span>", unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📋 Load Test Scenario")
    selected_scenario = st.selectbox(
        "Choose test case:",
        options=list(PRESETS.keys()),
        index=0,
        label_visibility="collapsed"
    )

# Top Bar
col_top_left, col_top_right = st.columns([7, 3])
with col_top_left:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
        <div class="brand-wordmark">
            <span class="chill">CHILL</span>GPT ⚡
        </div>
        <div class="nav-badge">
            PART 2: QUALITY CHECK & POLICY VALIDATION
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_top_right:
    theme_label = "🌙 Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Light Mode"
    theme_col1, theme_col2 = st.columns([1, 1])
    with theme_col2:
        if st.button(theme_label, use_container_width=True):
            st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
            st.rerun()

# Hero Section
st.markdown("""
<div class="hero-box">
    <div class="hero-tag"><span>⚡</span> RESPONSE QUALITY GUARDRULES</div>
    <h1 class="hero-title">AUDIT. VERIFY. <span class="hero-highlight">DE-ESCALATE.</span></h1>
    <p class="hero-sub">Detect false promises, identify missing order proof, evaluate tone, and output policy-backed responses.</p>
</div>
""", unsafe_allow_html=True)

preset_data = PRESETS[selected_scenario]

# Input Columns
col_in1, col_in2 = st.columns([1, 1], gap="medium")

with col_in1:
    st.markdown("""
    <div class="comic-panel-header">
        <div class="panel-label"><span>💥</span> 01 — THE SITUATION</div>
        <div class="sticker-tag sticker-tag-pink">COMPLAINT</div>
    </div>
    """, unsafe_allow_html=True)
    complaint_input = st.text_area(
        "Complaint Input",
        value=preset_data["complaint"],
        height=140,
        label_visibility="collapsed"
    )

    st.markdown("""
    <div class="comic-panel-header" style="margin-top: 14px;">
        <div class="panel-label"><span>📜</span> 02 — THE RULES</div>
        <div class="sticker-tag sticker-tag-yellow">POLICY</div>
    </div>
    """, unsafe_allow_html=True)
    policy_input = st.text_area(
        "Policy Input",
        value=preset_data["policy"],
        height=140,
        label_visibility="collapsed"
    )

with col_in2:
    st.markdown("""
    <div class="comic-panel-header">
        <div class="panel-label"><span>🤖</span> 03 — DRAFT TO AUDIT</div>
        <div class="sticker-tag sticker-tag-cyan">INITIAL AI RESPONSE</div>
    </div>
    """, unsafe_allow_html=True)
    response_input = st.text_area(
        "Draft Input",
        value=preset_data["response"],
        height=352,
        label_visibility="collapsed"
    )

# Action Button
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
review_clicked = st.button("AUDIT & VALIDATE RESPONSE ✦", type="primary", use_container_width=True)

if review_clicked or "review_results" in st.session_state:
    if review_clicked:
        with st.spinner("⚡ Running Quality Check..."):
            results = review_response(
                customer_complaint=complaint_input,
                company_policy=policy_input,
                generated_response=response_input,
                api_key=user_api_key if user_api_key else None
            )
            st.session_state["review_results"] = results
    else:
        results = st.session_state["review_results"]

    st.markdown("<hr style='border: 1.5px solid var(--border-color); margin: 30px 0;'>", unsafe_allow_html=True)

    status = results.get("compliance_status", "Non-Compliant")
    stamp_cls = "stamp-compliant" if status == "Compliant" else ("stamp-partially" if status == "Partially Compliant" else "stamp-noncompliant")
    mode = results.get("analysis_mode", "deterministic_fallback")
    mode_label = "🤖 Gemini AI Evaluation" if mode == "ai_gemini" else "⚙️ Deterministic Local Engine"

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div class="panel-label" style="font-size: 1.35rem;">
                <span>🛡️</span> QUALITY CHECK RESULTS
            </div>
            <div class="status-stamp {stamp_cls}">
                {status}
            </div>
        </div>
        <div class="sticker-tag sticker-tag-pink">{mode_label}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2-Column Audit Breakdown
    res_col1, res_col2 = st.columns(2, gap="medium")
    with res_col1:
        st.markdown("""
        <div class="comic-panel" style="padding: 16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:1rem; margin-bottom: 8px;">
                ⚖️ POLICY VIOLATIONS & FALSE PROMISES
            </div>
        """, unsafe_allow_html=True)
        violations = results.get("policy_violations", [])
        if violations:
            for v in violations:
                st.markdown(f"- ❌ **Violation**: {v}")
        else:
            st.markdown("✅ **No policy violations detected.**")

        fp_data = results.get("false_promises", {})
        fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"
        if fp_detected:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("⚠️ **False Promise Alert:**")
            for s in fp_data.get("suspicious_statements", []):
                st.markdown(f"> *\"{s}\"*")
        else:
            st.markdown("✅ **No false promises or unauthorized commitments.**")
        st.markdown("</div>", unsafe_allow_html=True)

    with res_col2:
        st.markdown("""
        <div class="comic-panel" style="padding: 16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:1rem; margin-bottom: 8px;">
                📋 REQUIRED INFORMATION AUDIT
            </div>
        """, unsafe_allow_html=True)
        missing = results.get("missing_information", [])
        if missing:
            for idx, item in enumerate(missing, 1):
                st.markdown(f"**{idx}. {item.get('item', 'Item')}** — *{item.get('reason', '')}*")
        else:
            st.markdown("✅ All necessary verification details requested.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Tone Scores (1-10)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
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
            <div class="tone-score-card">
                <div class="tone-score-val">{val}/10</div>
                <div class="tone-score-lbl">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(max(0.0, min(1.0, val / 10.0)))

    # Final Word Centerpiece
    st.markdown("<hr style='border: 1.5px solid var(--border-color); margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
    improved_text = results.get("improved_response", "")

    st.markdown(f"""
    <div class="final-word-container">
        <div class="final-word-header">
            <div class="final-word-title">
                <span>⚡</span> THE FINAL WORD ✦ READY TO SEND
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="sticker-tag sticker-tag-yellow">QUALITY AUDITED</span>
            </div>
        </div>
        <div class="final-speech-bubble">
{improved_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.code(improved_text, language="markdown")
