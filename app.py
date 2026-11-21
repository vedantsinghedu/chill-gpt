"""
ChillGPT — Your Little AI Support Companion
A Minimalist Creative Portfolio + Cute AI Companion Experience
Visual Identity: Warm Cream, Soft White, Lavender Accents, Playful Mascot "Chilly"
==============================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from typing import Dict, Any

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_TAGLINE,
    APP_ICON,
    get_custom_css,
    render_mascot_component,
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
    page_title=f"{APP_TITLE} ✦ {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Home"

# Inject Dynamic Portfolio Stylesheet
st.markdown(get_custom_css(st.session_state["theme_mode"]), unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. DATA INITIALIZATION & DEFAULTS
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
# 3. SIDEBAR: MINIMAL SECONDARY SETTINGS & QUICK PRESETS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 12px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 16px;">
        <div style="font-size: 1.1rem; font-weight: 800; letter-spacing: -0.02em;">
            ✨ COMPANION CONTROLS
        </div>
        <div style="font-size: 0.76rem; color: var(--text-muted); text-transform: uppercase;">
            Engine & Test Presets
        </div>
    </div>
    """, unsafe_allow_html=True)

    provider_option = st.selectbox(
        "LLM Engine",
        options=["Offline Simulator (Recommended for Demo)", "Google Gemini", "OpenAI / Compatible"],
        help="The Offline Simulator runs deterministic prompt engineering logic without requiring external API keys."
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
        model_name = st.text_input("Model Name", value="gpt-4o-mini")
        base_url = st.text_input("Base URL (Optional)", value="", placeholder="https://api.groq.com/openai/v1")
        provider_slug = "openai"
    else:
        provider_slug = "simulator"
        st.caption("🟢 Offline Simulator: Fast, deterministic, and free.")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Pre-Loaded Test Scenarios
    st.markdown("##### 📋 Quick Test Scenarios")
    scenario_titles = [c["title"] for c in sample_complaints]
    selected_scenario_title = st.selectbox("Select test scenario:", scenario_titles, key="scenario_selector", label_visibility="collapsed")

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
            st.session_state["active_nav"] = "Create Response"
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    temperature = st.slider(
        "Temperature (Grounding Rigor)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values enforce strict factual grounding."
    )

    st.divider()

    theme_label = "🌙 Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Light Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

# ------------------------------------------------------------------------------
# 4. CREATIVE PORTFOLIO TOP NAVIGATION BAR
# ------------------------------------------------------------------------------
nav_c1, nav_c2, nav_c3, nav_c4, nav_spacer, nav_theme = st.columns([1.8, 1.0, 1.4, 1.2, 2.0, 1.2], gap="small")

with nav_c1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; padding-top:4px;">
        <span style="font-size:1.25rem;">✨</span>
        <span style="font-weight:800; font-size:1.15rem; letter-spacing:-0.03em;">{APP_TITLE}</span>
        <span class="portfolio-pill-badge">COMPANION</span>
    </div>
    """, unsafe_allow_html=True)

with nav_c2:
    if st.button("✦ Home", use_container_width=True):
        st.session_state["active_nav"] = "Home"
        st.rerun()

with nav_c3:
    if st.button("✍️ Create Response", use_container_width=True):
        st.session_state["active_nav"] = "Create Response"
        st.rerun()

with nav_c4:
    if st.button("🛠️ Prompt Lab", use_container_width=True):
        st.session_state["active_nav"] = "Prompt Lab"
        st.rerun()

with nav_theme:
    mode_icon = "🌙" if st.session_state["theme_mode"] == "light" else "☀️"
    mode_txt = "Dark" if st.session_state["theme_mode"] == "light" else "Light"
    if st.button(f"{mode_icon} {mode_txt}", use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. VIEW: HOME SCREEN (INTERACTIVE PORTFOLIO INTRO)
# ------------------------------------------------------------------------------
if st.session_state["active_nav"] == "Home":
    st.markdown(f"""
    <div class="hero-editorial">
        <div class="hero-tagline">{APP_SUBTITLE}</div>
        <div class="hero-heading">Let's make things<br>a little better.</div>
        <div class="hero-sub">
            Turn customer grievances into calm, policy-perfect solutions with empathy and precision.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Chilly in peaceful greeting state via isolated iframe component
    components.html(render_mascot_component(
        state="idle",
        message="Hi! I'm Chilly. Tell me what happened — I've got you.",
        theme=st.session_state["theme_mode"]
    ), height=210)

    # Primary Hero CTA
    cta_c1, cta_c2, cta_c3 = st.columns([1, 1.4, 1])
    with cta_c2:
        if st.button("Create a Response ✦", type="primary", use_container_width=True):
            st.session_state["active_nav"] = "Create Response"
            st.rerun()

    st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

    # 4 Minimal Feature Pillars
    p1, p2, p3, p4 = st.columns(4, gap="medium")
    with p1:
        st.markdown("""
        <div style="background:var(--bg-card); padding:22px; border-radius:18px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:1.6rem; margin-bottom:8px;">🛡️</div>
            <div style="font-weight:700; font-size:0.98rem; margin-bottom:4px;">Policy Grounded</div>
            <div style="font-size:0.86rem; color:var(--text-secondary); line-height:1.4;">Zero hallucinations. Every statement is checked against terms.</div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown("""
        <div style="background:var(--bg-card); padding:22px; border-radius:18px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:1.6rem; margin-bottom:8px;">🌸</div>
            <div style="font-weight:700; font-size:0.98rem; margin-bottom:4px;">False Promise Shield</div>
            <div style="font-size:0.86rem; color:var(--text-secondary); line-height:1.4;">Detects unauthorized commitments before emails send.</div>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown("""
        <div style="background:var(--bg-card); padding:22px; border-radius:18px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:1.6rem; margin-bottom:8px;">🎭</div>
            <div style="font-weight:700; font-size:0.98rem; margin-bottom:4px;">3 Tone Personas</div>
            <div style="font-size:0.86rem; color:var(--text-secondary); line-height:1.4;">Steer smoothly between Professional, Friendly, and Empathetic.</div>
        </div>
        """, unsafe_allow_html=True)
    with p4:
        st.markdown("""
        <div style="background:var(--bg-card); padding:22px; border-radius:18px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:1.6rem; margin-bottom:8px;">✨</div>
            <div style="font-weight:700; font-size:0.98rem; margin-bottom:4px;">Part 2 Audit Engine</div>
            <div style="font-size:0.86rem; color:var(--text-secondary); line-height:1.4;">Automated compliance verification and tone scoring.</div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. VIEW: CREATE RESPONSE (INTERACTIVE WORKSPACE)
# ------------------------------------------------------------------------------
elif st.session_state["active_nav"] == "Create Response":
    has_generated = bool(st.session_state["analysis_result"] and st.session_state["draft_response"])

    # Determine Mascot State & Message
    if not has_generated:
        if len(st.session_state["complaint_area"].strip()) > 10:
            mascot_state = "listening"
            mascot_msg = "I'm listening! When you're ready, click 'Make it Chill ✦'."
        else:
            mascot_state = "idle"
            mascot_msg = "Tell me what happened. I've got you."
    else:
        mascot_state = "success"
        mascot_msg = "All sorted! Here is a calm, policy-perfect response ✦"

    # Central Mascot Stage
    components.html(render_mascot_component(
        state=mascot_state,
        message=mascot_msg,
        theme=st.session_state["theme_mode"]
    ), height=210)

    # --------------------------------------------------------------------------
    # INPUT EXPERIENCE: COMPACT, ELEGANT, CONVERSATIONAL
    # --------------------------------------------------------------------------
    st.markdown("""
    <div style="text-align: center; margin-bottom: 14px;">
        <div style="font-family:'Playfair Display', serif; font-size: 1.45rem; font-weight: 600;">
            Okay, tell me what happened...
        </div>
        <div style="font-size: 0.9rem; color: var(--text-secondary);">
            Paste the customer's grievance, email, or question below.
        </div>
    </div>
    """, unsafe_allow_html=True)

    complaint_text = st.text_area(
        label="Customer Complaint",
        key="complaint_area",
        height=140,
        label_visibility="collapsed",
        placeholder="Paste customer grievance, angry email, or return request here..."
    )

    # Policy Input in a Soft, Elegant Expander (Does not dominate screen)
    with st.expander("📋 Company Policy Guidelines (Grounding Terms)", expanded=False):
        policy_text = st.text_area(
            label="Company Policy",
            key="policy_area",
            height=110,
            label_visibility="collapsed",
            placeholder="Store terms, warranty rules, return conditions..."
        )
        st.caption("🛡️ The response will be strictly grounded against these rules.")
    policy_text = st.session_state["policy_area"]

    # Centered Tone Selection
    st.markdown("""
    <div style="text-align: center; margin-top: 14px; margin-bottom: 6px;">
        <span style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
            Select Response Tone
        </span>
    </div>
    """, unsafe_allow_html=True)

    current_tone = st.radio(
        label="Response Tone",
        options=["Professional", "Friendly", "Empathetic"],
        index=["Professional", "Friendly", "Empathetic"].index(st.session_state["selected_tone"]),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state["selected_tone"] = current_tone

    # Primary Action Button
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    cta_col1, cta_col2, cta_col3 = st.columns([1, 1.6, 1])
    with cta_col2:
        generate_btn = st.button("MAKE IT CHILL ✦", type="primary", use_container_width=True)

    # --------------------------------------------------------------------------
    # PIPELINE EXECUTION
    # --------------------------------------------------------------------------
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
            st.error("⚠️ Please describe the customer grievance before generating.")
        elif not policy_text.strip():
            st.error("⚠️ Please provide company policy terms for grounding.")
        else:
            with st.spinner("✨ Chilly is analyzing the complaint and checking policy rules..."):
                try:
                    analysis = analyzer.analyze(complaint_text=complaint_text, company_policy=policy_text)
                    st.session_state["analysis_result"] = analysis
                except Exception as e:
                    st.error(f"❌ Complaint Analysis Failed: {str(e)}")
                    st.stop()

            with st.spinner(f"✍️ Drafting response in '{st.session_state['selected_tone']}' tone..."):
                try:
                    draft = generator.generate_response(
                        complaint_text=complaint_text,
                        company_policy=policy_text,
                        analysis_data=st.session_state["analysis_result"],
                        tone=st.session_state["selected_tone"],
                        temperature=temperature
                    )
                    st.session_state["draft_response"] = draft

                    # Package handoff internally for Part 2 Reviewer
                    handoff_pkg = create_handoff_package(
                        complaint_text=complaint_text,
                        company_policy=policy_text,
                        analysis=st.session_state["analysis_result"],
                        tone=st.session_state["selected_tone"],
                        draft_response=draft,
                        model_name=client.model_name
                    )
                    st.session_state["handoff_data"] = handoff_pkg.to_dict()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Response Generation Failed: {str(e)}")
                    st.stop()

    # --------------------------------------------------------------------------
    # RESULTS EXPERIENCE: CLEAN READING CANVAS + THE QUALITY CHECK
    # --------------------------------------------------------------------------
    if st.session_state["analysis_result"] and st.session_state["draft_response"]:
        analysis = st.session_state["analysis_result"]
        draft = st.session_state["draft_response"]

        # Run Part 2 Quality Audit
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

        with st.spinner("Checking response compliance against policy rules..."):
            audit_res = reviewer.validate_draft(handoff_obj, api_key=review_api_key)

        status = audit_res.get("compliance_status", "Non-Compliant")
        chip_class = "chip-compliant" if status == "Compliant" else ("chip-partially" if status == "Partially Compliant" else "chip-noncompliant")
        final_response_text = audit_res.get("improved_response") if status != "Compliant" and audit_res.get("improved_response") else draft

        st.markdown("<hr style='border: 1px solid var(--border-color); margin: 32px 0 20px 0;'>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 1. NEW FEATURE: CUSTOMER GRIEVANCE & TONE INTELLIGENCE ANALYSIS
        # ----------------------------------------------------------------------
        details = analysis.get("important_details", {})
        grounding = analysis.get("policy_grounding", {})
        sentiment = analysis.get("sentiment", "Frustrated")
        intensity = analysis.get("sentiment_intensity", 7)
        rationale = analysis.get("sentiment_rationale", "")
        category = analysis.get("category", "General Inquiry")
        main_issue = analysis.get("main_issue", "")
        order_id = details.get("order_id", "Not provided")
        product_name = details.get("product_name", "Not provided")
        demands = details.get("demands_made", [])
        unsupported = grounding.get("unsupported_demands", [])

        # Tone and Escalation Classification
        if sentiment in ["Angry", "Furious"]:
            badge_cls = "badge-frustrated"
            tone_label = "Angry / Hostile"
            urgency_level = "High Priority"
            risk_label = "🚨 High Escalation Risk"
        elif sentiment in ["Frustrated"]:
            badge_cls = "badge-frustrated"
            tone_label = "Frustrated / Dissatisfied"
            urgency_level = "Elevated"
            risk_label = "⚡ Friction Detected"
        elif sentiment in ["Anxious", "Worried"]:
            badge_cls = "badge-anxious"
            tone_label = "Anxious / Time-Sensitive"
            urgency_level = "Urgent"
            risk_label = "⚠️ Urgent Assistance"
        elif sentiment in ["Disappointed"]:
            badge_cls = "badge-disappointed"
            tone_label = "Disappointed / Let Down"
            urgency_level = "Moderate"
            risk_label = "🌿 Retention Risk"
        else:
            badge_cls = "badge-neutral"
            tone_label = "Neutral / Direct"
            urgency_level = "Standard"
            risk_label = "🟢 Low Risk"

        demands_str = ", ".join(demands) if demands else "General assistance or resolution"
        policy_status_str = f"⚠️ Demands out-of-policy: {', '.join(unsupported)}" if unsupported else "✅ Demands are covered by company terms"

        st.markdown(f"""
        <div class="intelligence-card">
            <div class="intelligence-header">
                <div class="intelligence-title">
                    <span>🔍</span> Customer Grievance & Tone Analysis
                </div>
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <span class="emotion-badge {badge_cls}">{sentiment.upper()} ({intensity}/10)</span>
                    <span class="portfolio-pill-badge">{risk_label}</span>
                </div>
            </div>
            <div style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.5;">
                <strong>Customer Emotional Tone:</strong> Customer communicates in a <em>{tone_label}</em> manner. {rationale}
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-bottom: 18px;">
                <div class="metric-tile">
                    <div class="metric-tile-label">Customer Emotion</div>
                    <div class="metric-tile-value">💬 {sentiment} ({intensity}/10)</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">Urgency Assessment</div>
                    <div class="metric-tile-value">⏱️ {urgency_level}</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">Complaint Category</div>
                    <div class="metric-tile-value">🏷️ {category}</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">Order Identifier</div>
                    <div class="metric-tile-value">📦 {order_id}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px;">
                <div style="background: var(--bg-card-alt); border: 1px solid var(--border-color); border-radius: 14px; padding: 16px 18px;">
                    <div class="metric-tile-label">Core Pain Point & Root Cause</div>
                    <div style="font-weight: 600; font-size: 0.98rem; margin-top: 4px; line-height: 1.5; color: var(--text-primary);">
                        {main_issue}
                    </div>
                </div>
                <div style="background: var(--bg-card-alt); border: 1px solid var(--border-color); border-radius: 14px; padding: 16px 18px;">
                    <div class="metric-tile-label">Customer Demands & Policy Grounding</div>
                    <div style="font-size: 0.92rem; margin-top: 4px; line-height: 1.5;">
                        <strong>Demands:</strong> {demands_str}
                    </div>
                    <div style="font-size: 0.9rem; margin-top: 4px; color: var(--text-secondary);">
                        <strong>Policy Alignment:</strong> {policy_status_str}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # 2. FINAL RESPONSE READING CANVAS
        # ----------------------------------------------------------------------
        st.markdown(f"""
        <div class="reading-canvas">
            <div class="reading-canvas-header">
                <div class="reading-canvas-title">
                    <span>✨</span> Your Response is Ready
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="status-chip chip-compliant">{st.session_state['selected_tone'].upper()} TONE</span>
                    <span class="status-chip {chip_class}">{status}</span>
                </div>
            </div>
            <div class="reading-canvas-body">
{final_response_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 1-Click Copy and Start Fresh (Re-Draft removed as requested)
        act_col1, act_col2 = st.columns([1.5, 1.0], gap="medium")
        with act_col1:
            copy_html = f"""
            <button id="copyBtn" onclick="copyText()" style="
                background: #262422;
                color: #FFFFFF;
                border: none;
                border-radius: 999px;
                padding: 12px 24px;
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 0.95rem;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 4px 14px rgba(0,0,0,0.12);
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s ease;
                width: 100%;
                justify-content: center;
            ">
                <span id="copyIcon">📋</span> <span id="copyLabel">Copy Response</span>
            </button>
            <script>
            function copyText() {{
                const text = {json.dumps(final_response_text)};
                navigator.clipboard.writeText(text).then(() => {{
                    const btn = document.getElementById('copyBtn');
                    const icon = document.getElementById('copyIcon');
                    const label = document.getElementById('copyLabel');
                    btn.style.background = '#059669';
                    icon.innerText = '✅';
                    label.innerText = 'Copied to Clipboard!';
                    setTimeout(() => {{
                        btn.style.background = '#262422';
                        icon.innerText = '📋';
                        label.innerText = 'Copy Response';
                    }}, 2500);
                }}).catch(err => console.error(err));
            }}
            </script>
            """
            components.html(copy_html, height=54)

        with act_col2:
            if st.button("Start Fresh ↺", use_container_width=True):
                st.session_state["analysis_result"] = None
                st.session_state["draft_response"] = None
                st.session_state["handoff_data"] = None
                st.rerun()

        # Compare Initial Draft
        with st.expander("👁️ Compare with Original Draft (Part 1 Baseline)"):
            st.markdown(f"""
            <div style="background:var(--bg-card-alt); padding:20px; border-radius:16px; border:1px solid var(--border-color); font-size:1rem; line-height:1.7;">
{draft}
            </div>
            """, unsafe_allow_html=True)

        # 2. THE QUALITY CHECK (PART 2 VALIDATION)
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        with st.expander("🛡️ The Quality Check (Policy & Tone Validation)", expanded=True):
            qc_c1, qc_c2 = st.columns(2, gap="medium")
            with qc_c1:
                violations = audit_res.get("policy_violations", [])
                fp_data = audit_res.get("false_promises", {})
                fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"

                st.markdown("**Policy Violations & Commitments**")
                if violations:
                    for v in violations:
                        st.markdown(f"""
                        <div class="alert-container-danger">
                            <strong>Policy Concern:</strong> {v}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert-container-success">
                        ✅ <strong>100% Policy Grounded:</strong> No violations found.
                    </div>
                    """, unsafe_allow_html=True)

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
                        ✅ <strong>Zero False Promises:</strong> No unauthorized guarantees.
                    </div>
                    """, unsafe_allow_html=True)

            with qc_c2:
                missing = audit_res.get("missing_information", [])
                st.markdown("**Required Customer Details**")
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
                        ✅ All necessary customer verification details requested.
                    </div>
                    """, unsafe_allow_html=True)

            # Tone Scores
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            scores = audit_res.get("tone_scores", {})
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

# ------------------------------------------------------------------------------
# 7. VIEW: PROMPT LAB (BEHIND THE SCENES)
# ------------------------------------------------------------------------------
elif st.session_state["active_nav"] == "Prompt Lab":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <div class="hero-tagline">BEHIND THE SCENES</div>
        <div class="hero-heading" style="font-size: 2.2rem;">Prompt Engineering Lab</div>
        <div class="hero-sub">
            Inspect the underlying system prompts, few-shot grounding directives, and telemetry data.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("1. Core System Prompt & Grounding Directives", expanded=True):
        st.code(CORE_SYSTEM_PROMPT, language="markdown")

    with st.expander("2. Complaint Analysis Prompt Template"):
        st.code(ANALYSIS_USER_PROMPT, language="markdown")

    with st.expander(f"3. Tone Steering Directive Applied ({st.session_state['selected_tone']})"):
        st.code(TONE_DIRECTIVES.get(st.session_state["selected_tone"], ""), language="markdown")

    with st.expander("4. Response Generation Prompt Template"):
        st.code(RESPONSE_USER_PROMPT, language="markdown")

    if st.session_state["handoff_data"]:
        with st.expander("5. Live Audit Telemetry Payload"):
            st.json(st.session_state["handoff_data"])

# ------------------------------------------------------------------------------
# 8. MINIMAL PORTFOLIO FOOTER
# ------------------------------------------------------------------------------
st.markdown(f"""
<div class="portfolio-footer">
    <div class="portfolio-footer-brand">
        <span>✨</span> {APP_TITLE} · {APP_SUBTITLE}
    </div>
    <div>
        Crafted with empathy & precision · 2026
    </div>
</div>
""", unsafe_allow_html=True)
