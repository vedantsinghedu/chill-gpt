"""
ChillGPT – Customer Support Response Assistant
Visual Identity: Comic-Book Pop Art × Editorial Collage × Gen-Z Creative Studio
==============================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from typing import Dict, Any

from config import (
    APP_TITLE,
    APP_TAGLINE,
    APP_STUDIO_LABEL,
    APP_ICON,
    get_custom_css,
    load_sample_policies,
    load_sample_complaints
)
from modules.llm_client import LLMClient
from modules.analyzer import ComplaintAnalyzer
from modules.generator import ResponseGenerator
from modules.reviewer_interface import create_handoff_package, ChillGPTReviewer, DraftResponseHandoff
from modules.prompts import (
    CORE_SYSTEM_PROMPT,
    ANALYSIS_USER_PROMPT,
    RESPONSE_USER_PROMPT,
    TONE_DIRECTIVES
)

# ------------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_TITLE} ✦ {APP_TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Theme Mode in Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"

# Inject Dynamic CSS (Light or Dark Theme)
st.markdown(get_custom_css(st.session_state["theme_mode"]), unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. SESSION STATE & DATA INITIALIZATION
# ------------------------------------------------------------------------------
sample_policies = load_sample_policies()
sample_complaints = load_sample_complaints()

default_policy = sample_policies[0]["text"] if sample_policies else ""
default_complaint = sample_complaints[0]["text"] if sample_complaints else ""

if "complaint_area" not in st.session_state:
    st.session_state["complaint_area"] = default_complaint
if "policy_area" not in st.session_state:
    st.session_state["policy_area"] = default_policy
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "draft_response" not in st.session_state:
    st.session_state["draft_response"] = None
if "handoff_data" not in st.session_state:
    st.session_state["handoff_data"] = None
if "selected_tone" not in st.session_state:
    st.session_state["selected_tone"] = "Professional"

# ------------------------------------------------------------------------------
# 3. SIDEBAR CONFIGURATION (COMPACT, POLISHED, NO ACADEMIC CLUTTER)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 10px 0 16px 0; border-bottom: 2px solid var(--border-color); margin-bottom: 16px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 900; letter-spacing: -0.02em;">
            ⚡ STUDIO CONTROLS
        </div>
        <div style="font-family: 'Space Mono', monospace; font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">
            Engine Setup & Presets
        </div>
    </div>
    """, unsafe_allow_html=True)

    provider_option = st.selectbox(
        "🧠 LLM Engine",
        options=["Offline Simulator (Recommended for Demo)", "Google Gemini", "OpenAI / Compatible"],
        help="The Offline Simulator executes the exact prompt engineering extraction and generation logic deterministically without requiring an external API key."
    )

    api_key = ""
    model_name = ""
    base_url = ""

    if provider_option == "Google Gemini":
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key.")
        model_name = st.selectbox("Gemini Model", ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"])
        provider_slug = "gemini"
    elif provider_option == "OpenAI / Compatible":
        api_key = st.text_input("API Key", type="password", help="OpenAI or custom provider key.")
        model_name = st.text_input("Model Name", value="gpt-4o-mini", help="E.g. gpt-4o-mini, llama-3.3-70b-versatile, etc.")
        base_url = st.text_input("Custom Base URL (Optional)", value="", placeholder="https://api.groq.com/openai/v1")
        provider_slug = "openai"
    else:
        provider_slug = "simulator"
        st.markdown("""
        <div style="background: var(--bg-panel); border: 2px solid var(--border-color); padding: 8px 12px; margin-bottom: 12px; box-shadow: 2px 2px 0px var(--shadow-color); font-size: 0.8rem; font-weight: 600;">
            ⚡ Offline Simulator Active (Zero API cost & deterministic prompt logic)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Pre-Loaded Test Scenarios
    st.markdown("##### 📋 Quick Test Scenarios")
    scenario_titles = [c["title"] for c in sample_complaints]
    selected_scenario_title = st.selectbox("Load sample case:", scenario_titles, key="scenario_selector", label_visibility="collapsed")

    if st.button("📥 Load Scenario", use_container_width=True):
        matched_complaint = next((c for c in sample_complaints if c["title"] == selected_scenario_title), None)
        if matched_complaint:
            st.session_state["complaint_area"] = matched_complaint["text"]
            policy_id = matched_complaint.get("policy_id")
            matched_policy = next((p for p in sample_policies if p["id"] == policy_id), None)
            if matched_policy:
                st.session_state["policy_area"] = matched_policy["text"]

            st.session_state["analysis_result"] = None
            st.session_state["draft_response"] = None
            st.session_state["handoff_data"] = None
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    temperature = st.slider(
        "Temperature (Grounding Control)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values enforce strict factual grounding and policy adherence."
    )

# ------------------------------------------------------------------------------
# 4. TOP BRANDING BAR & THEME SWITCHER
# ------------------------------------------------------------------------------
col_top_left, col_top_right = st.columns([7, 3])

with col_top_left:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
        <div class="brand-wordmark">
            <span class="chill">CHILL</span>GPT ⚡
        </div>
        <div class="nav-badge">
            {APP_STUDIO_LABEL}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_top_right:
    # Theme Toggle Button
    theme_label = "🌙 Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Light Mode"
    theme_btn_col1, theme_btn_col2 = st.columns([1, 1])
    with theme_btn_col2:
        if st.button(theme_label, use_container_width=True):
            st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
            st.rerun()

# Hero Section
st.markdown(f"""
<div class="hero-box">
    <div class="hero-tag"><span>⚡</span> NEXT-GEN SUPPORT COPILOT</div>
    <h1 class="hero-title">TURN COMPLAINTS <span class="hero-highlight">INTO WINS.</span></h1>
    <p class="hero-sub">{APP_TAGLINE} Empathetic, policy-backed customer responses generated in seconds. Zero drama, 100% compliant.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. MAIN WORKSPACE: 01 — THE SITUATION & 02 — THE RULES
# ------------------------------------------------------------------------------
col_sit, col_rules = st.columns([1, 1], gap="medium")

with col_sit:
    st.markdown("""
    <div class="comic-panel-header">
        <div class="panel-label">
            <span>💥</span> 01 — THE SITUATION
        </div>
        <div class="sticker-tag sticker-tag-pink">CUSTOMER COMPLAINT</div>
    </div>
    """, unsafe_allow_html=True)
    complaint_text = st.text_area(
        label="Customer Complaint Input",
        key="complaint_area",
        height=220,
        label_visibility="collapsed",
        placeholder="Paste customer grievance, angry email, or return request here..."
    )
    st.caption(f"📝 Length: **{len(complaint_text)}** characters | **{len(complaint_text.split())}** words")

with col_rules:
    st.markdown("""
    <div class="comic-panel-header">
        <div class="panel-label">
            <span>📜</span> 02 — THE RULES
        </div>
        <div class="sticker-tag sticker-tag-yellow">GROUNDING POLICY</div>
    </div>
    """, unsafe_allow_html=True)
    policy_text = st.text_area(
        label="Company Policy Input",
        key="policy_area",
        height=220,
        label_visibility="collapsed",
        placeholder="Paste store terms, return policy, warranty guidelines, or refund rules..."
    )
    st.caption(f"🛡️ Guardrails: **{len(policy_text.splitlines())}** policy clauses active")

# ------------------------------------------------------------------------------
# 6. TONE SELECTOR & ACTION CTA
# ------------------------------------------------------------------------------
st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

tone_panel_col, action_col1, action_col2 = st.columns([2.2, 1.8, 0.8], gap="medium")

with tone_panel_col:
    st.markdown("**🎭 SELECT RESPONSE VIBE:**")
    current_tone = st.radio(
        label="Response Tone Selector",
        options=["Professional", "Friendly", "Empathetic"],
        index=["Professional", "Friendly", "Empathetic"].index(st.session_state["selected_tone"]),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state["selected_tone"] = current_tone

with action_col1:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button(
        "MAKE IT CHILL ✦",
        type="primary",
        use_container_width=True,
        help="Analyze complaint, ground against policy, draft response, and validate!"
    )

with action_col2:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    clear_btn = st.button("RESET ↺", use_container_width=True)
    if clear_btn:
        st.session_state["analysis_result"] = None
        st.session_state["draft_response"] = None
        st.session_state["handoff_data"] = None
        st.rerun()

# ------------------------------------------------------------------------------
# 7. EXECUTION PIPELINE (ANALYSIS + GENERATION + PART 2 VALIDATION)
# ------------------------------------------------------------------------------
client = LLMClient(
    provider=provider_slug,
    api_key=api_key,
    model_name=model_name,
    base_url=base_url
)
analyzer = ComplaintAnalyzer(llm_client=client)
generator = ResponseGenerator(llm_client=client)

if generate_btn:
    if not complaint_text.strip():
        st.error("⚠️ Please enter a customer complaint before generating.")
    elif not policy_text.strip():
        st.error("⚠️ Please enter company policy terms for grounding.")
    else:
        with st.spinner("⚡ Analyzing complaint & policy grounding..."):
            try:
                analysis = analyzer.analyze(complaint_text=complaint_text, company_policy=policy_text)
                st.session_state["analysis_result"] = analysis
            except Exception as e:
                st.error(f"❌ Complaint Analysis Failed: {str(e)}")
                st.stop()

        with st.spinner(f"✍️ Drafting response in '{st.session_state['selected_tone']}' vibe..."):
            try:
                draft = generator.generate_response(
                    complaint_text=complaint_text,
                    company_policy=policy_text,
                    analysis_data=st.session_state["analysis_result"],
                    tone=st.session_state["selected_tone"],
                    temperature=temperature
                )
                st.session_state["draft_response"] = draft

                # Package official handoff internally for Part 2 Reviewer
                handoff_pkg = create_handoff_package(
                    complaint_text=complaint_text,
                    company_policy=policy_text,
                    analysis=st.session_state["analysis_result"],
                    tone=st.session_state["selected_tone"],
                    draft_response=draft,
                    model_name=client.model_name
                )
                st.session_state["handoff_data"] = handoff_pkg.to_dict()

            except Exception as e:
                st.error(f"❌ Response Generation Failed: {str(e)}")
                st.stop()

# ------------------------------------------------------------------------------
# 8. OUTPUT DASHBOARD: COMPLAINT ANALYSIS + ORIGINAL DRAFT + QUALITY CHECK + FINAL WORD
# ------------------------------------------------------------------------------
if st.session_state["analysis_result"] and st.session_state["draft_response"]:
    analysis = st.session_state["analysis_result"]
    draft = st.session_state["draft_response"]
    details = analysis.get("important_details", {})
    grounding = analysis.get("policy_grounding", {})
    missing_info = analysis.get("missing_information", [])

    st.markdown("<hr style='border: 1.5px solid var(--border-color); margin: 30px 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION A: COMPLAINT ANALYSIS (03 — THE BREAKDOWN)
    # ==========================================================================
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
        <div class="panel-label" style="font-size: 1.35rem;">
            <span>🎯</span> 03 — THE BREAKDOWN
        </div>
        <div class="sticker-tag sticker-tag-yellow">COMPLAINT INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Punchy Metric Cards
    m1, m2, m3, m4 = st.columns(4)

    sentiment = analysis.get("sentiment", "Neutral")
    intensity = analysis.get("sentiment_intensity", 5)
    badge_cls = f"badge-{sentiment.lower()}" if sentiment.lower() in ["angry", "frustrated", "anxious", "disappointed", "neutral"] else "badge-neutral"

    with m1:
        st.markdown(f"""
        <div class="analysis-metric-card">
            <div class="metric-super-title">Customer Sentiment</div>
            <div class="metric-bold-value"><span class="{badge_cls}">{sentiment} ({intensity}/10)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="analysis-metric-card">
            <div class="metric-super-title">Complaint Category</div>
            <div class="metric-bold-value">🏷️ {analysis.get("category", "General")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="analysis-metric-card">
            <div class="metric-super-title">Order Identifier</div>
            <div class="metric-bold-value">📦 {details.get("order_id", "Not provided")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        unsupported = grounding.get("unsupported_demands", [])
        status_txt = "⚠️ Out-of-Policy" if unsupported else "✅ Grounded"
        status_c = "var(--accent-pink)" if unsupported else "var(--accent-green)"
        st.markdown(f"""
        <div class="analysis-metric-card">
            <div class="metric-super-title">Policy Grounding</div>
            <div class="metric-bold-value" style="color: {status_c};">{status_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Detailed Analysis breakdown
    det_col1, det_col2 = st.columns([1, 1], gap="medium")
    with det_col1:
        st.markdown(f"""
        <div class="comic-panel" style="padding: 16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight: 800; font-size: 1rem; margin-bottom: 8px;">
                🎯 MAIN ISSUE & RATIONALE
            </div>
            <p style="margin: 0 0 10px 0; font-weight: 600;">{analysis.get("main_issue", "No summary.")}</p>
            <p style="margin: 0; font-size: 0.88rem; color: var(--text-secondary);">{analysis.get("sentiment_rationale", "")}</p>
        </div>
        """, unsafe_allow_html=True)

    with det_col2:
        st.markdown(f"""
        <div class="comic-panel" style="padding: 16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight: 800; font-size: 1rem; margin-bottom: 8px;">
                🛡️ GROUNDING RULES APPLIED
            </div>
            <div style="font-size: 0.88rem; margin-bottom: 6px;">
                <strong>Declined Demands:</strong> {", ".join(grounding.get("unsupported_demands", [])) or "None; fits within policy"}
            </div>
            <div style="font-size: 0.88rem;">
                <strong>Approved Actions:</strong> {", ".join(grounding.get("supported_actions", [])) or "Standard helpful assistance"}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION B: PART 2 RESPONSE REVIEW & POLICY VALIDATION (THE QUALITY CHECK)
    # ==========================================================================
    handoff_dict = st.session_state["handoff_data"]
    handoff_obj = DraftResponseHandoff(
        complaint_text=handoff_dict["complaint_text"],
        company_policy=handoff_dict["company_policy"],
        analysis=handoff_dict["analysis"],
        tone=handoff_dict["tone"],
        draft_response=handoff_dict["draft_response"],
        metadata=handoff_dict.get("metadata", {})
    )

    reviewer = ChillGPTReviewer()
    review_api_key = api_key if provider_slug == "gemini" and api_key else os.environ.get("GEMINI_API_KEY", "")

    with st.spinner("⚡ Running Quality Check (Policy compliance, false promises & tone)..."):
        audit_res = reviewer.validate_draft(handoff_obj, api_key=review_api_key)

    st.markdown("<hr style='border: 1.5px solid var(--border-color); margin: 30px 0;'>", unsafe_allow_html=True)

    status = audit_res.get("compliance_status", "Non-Compliant")
    stamp_cls = "stamp-compliant" if status == "Compliant" else ("stamp-partially" if status == "Partially Compliant" else "stamp-noncompliant")
    mode_text = "🤖 Gemini AI Evaluation" if audit_res.get("analysis_mode") == "ai_gemini" else "⚙️ Deterministic Local Engine"

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div class="panel-label" style="font-size: 1.35rem;">
                <span>🛡️</span> 04 — THE QUALITY CHECK
            </div>
            <div class="status-stamp {stamp_cls}">
                {status}
            </div>
        </div>
        <div class="sticker-tag sticker-tag-pink">{mode_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Audit Overview Panel (Violations, False Promises, Missing Info)
    col_q1, col_q2 = st.columns([1, 1], gap="medium")

    with col_q1:
        violations = audit_res.get("policy_violations", [])
        fp_data = audit_res.get("false_promises", {})
        fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"

        st.markdown("""
        <div class="comic-panel" style="padding: 16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:1rem; margin-bottom: 8px;">
                ⚖️ POLICY VIOLATIONS & FALSE PROMISES
            </div>
        """, unsafe_allow_html=True)

        if violations:
            for v in violations:
                st.markdown(f"- ❌ **Violation**: {v}")
        else:
            st.markdown("✅ **Zero policy violations** detected in the draft.")

        if fp_detected:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("⚠️ **False Promise Alert:**")
            for s in fp_data.get("suspicious_statements", []):
                st.markdown(f"> *\"{s}\"*")
        else:
            st.markdown("✅ **No unauthorized commitments or false promises.**")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_q2:
        missing = audit_res.get("missing_information", [])
        st.markdown("""
        <div class="comic-panel" style="padding: 16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:1rem; margin-bottom: 8px;">
                📋 REQUIRED INFORMATION AUDIT
            </div>
        """, unsafe_allow_html=True)

        if missing:
            for idx, m in enumerate(missing, 1):
                st.markdown(f"**{idx}. {m.get('item', 'Detail')}** — *{m.get('reason', '')}*")
        else:
            st.markdown("✅ All necessary verification details requested from the customer.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Tone Scores Display (5 Dimensions: 1-10 Scale)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    tone_scores = audit_res.get("tone_scores", {})
    sc_cols = st.columns(5)
    metrics_meta = [
        ("Professionalism", tone_scores.get("professionalism", 7)),
        ("Empathy", tone_scores.get("empathy", 5)),
        ("Politeness", tone_scores.get("politeness", 6)),
        ("Clarity", tone_scores.get("clarity", 7)),
        ("Friendliness", tone_scores.get("customer_friendliness", 6)),
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

    # ==========================================================================
    # SECTION C: ORIGINAL DRAFT VS. THE FINAL WORD (CENTERPIECE)
    # ==========================================================================
    st.markdown("<hr style='border: 1.5px solid var(--border-color); margin: 34px 0 24px 0;'>", unsafe_allow_html=True)

    # Expandable Original Draft
    with st.expander("👀 View Original Draft (Part 1 Initial AI Generation)"):
        st.markdown(f"""
        <div class="original-draft-box">
{draft}
        </div>
        """, unsafe_allow_html=True)

    # CENTERPIECE: THE FINAL WORD
    final_response_text = audit_res.get("improved_response") if status != "Compliant" and audit_res.get("improved_response") else draft

    st.markdown(f"""
    <div class="final-word-container">
        <div class="final-word-header">
            <div class="final-word-title">
                <span>⚡</span> THE FINAL WORD ✦ READY TO SEND
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="sticker-tag sticker-tag-yellow">{st.session_state['selected_tone']} TONE</span>
                <span class="sticker-tag sticker-tag-cyan">VERIFIED RESPONSE</span>
            </div>
        </div>
        <div class="final-speech-bubble">
{final_response_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Copy Button (Interactive HTML/JS with Visual Feedback)
    copy_col1, copy_col2 = st.columns([1, 1])
    with copy_col1:
        copy_html = f"""
        <button id="copyFinalBtn" onclick="copyFinalResponse()" style="
            background-color: var(--accent-yellow);
            color: #111111;
            border: 2.5px solid var(--border-color);
            padding: 10px 22px;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1rem;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 4px 4px 0px var(--shadow-color);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.12s ease;
        ">
            <span id="copyIcon">📋</span> <span id="copyText">COPY FINAL RESPONSE</span>
        </button>
        <script>
        function copyFinalResponse() {{
            const text = {json.dumps(final_response_text)};
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copyFinalBtn');
                const icon = document.getElementById('copyIcon');
                const label = document.getElementById('copyText');
                btn.style.backgroundColor = '#4ADE80';
                icon.innerText = '✅';
                label.innerText = 'COPIED TO CLIPBOARD!';
                setTimeout(() => {{
                    btn.style.backgroundColor = 'var(--accent-yellow)';
                    icon.innerText = '📋';
                    label.innerText = 'COPY FINAL RESPONSE';
                }}, 2500);
            }}).catch(err => console.error(err));
        }}
        </script>
        """
        components.html(copy_html, height=52)

    with copy_col2:
        if st.button(f"🔄 Re-Draft in '{st.session_state['selected_tone']}'", use_container_width=True):
            with st.spinner("Re-drafting..."):
                new_draft = generator.generate_response(
                    complaint_text=complaint_text,
                    company_policy=policy_text,
                    analysis_data=st.session_state["analysis_result"],
                    tone=st.session_state["selected_tone"],
                    temperature=temperature
                )
                st.session_state["draft_response"] = new_draft
                handoff_pkg = create_handoff_package(
                    complaint_text=complaint_text,
                    company_policy=policy_text,
                    analysis=st.session_state["analysis_result"],
                    tone=st.session_state["selected_tone"],
                    draft_response=new_draft,
                    model_name=client.model_name
                )
                st.session_state["handoff_data"] = handoff_pkg.to_dict()
                st.rerun()

    # ==========================================================================
    # SECTION D: PROMPT LAB (BEHIND THE RESPONSE — COLLAPSED BY DEFAULT)
    # ==========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("✦ BEHIND THE RESPONSE — PROMPT LAB (ACADEMIC GRADING INSPECTOR)"):
        st.markdown("##### 1. System Prompt & Grounding Guardrails")
        st.code(CORE_SYSTEM_PROMPT, language="markdown")

        st.markdown("##### 2. Complaint Analysis Prompt Template")
        st.code(ANALYSIS_USER_PROMPT, language="markdown")

        st.markdown(f"##### 3. Tone Steering Directive Applied ({st.session_state['selected_tone']})")
        st.code(TONE_DIRECTIVES.get(st.session_state["selected_tone"], ""), language="markdown")

        st.markdown("##### 4. Response Generation Prompt Template")
        st.code(RESPONSE_USER_PROMPT, language="markdown")

        st.markdown("##### 5. Part 2 Reviewer Output Payload")
        st.json(audit_res)
