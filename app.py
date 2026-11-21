"""
ChillGPT – Customer Support Response Assistant
Professional Enterprise Complaint Management & Response Assistant
Visual Identity: Clean Modern SaaS, Fluid Navigation, Refined Motion & Accessible Contrast
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
    page_title=f"{APP_TITLE} | {APP_SUBTITLE}",
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
# 3. SIDEBAR CONFIGURATION (PROFESSIONAL CONTROLS)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid var(--border-color); margin-bottom: 16px;">
        <div style="font-size: 1.05rem; font-weight: 800; letter-spacing: -0.02em;">
            ⚙️ ENGINE & SCENARIOS
        </div>
        <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
            System Settings
        </div>
    </div>
    """, unsafe_allow_html=True)

    provider_option = st.selectbox(
        "LLM Engine",
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
        st.caption("🟢 Offline Simulator: Fast, deterministic, and 100% free.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Pre-Loaded Test Scenarios
    st.markdown("##### 📋 Load Pre-configured Case")
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
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    temperature = st.slider(
        "Temperature (Grounding Rigor)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values enforce strict factual grounding and policy adherence."
    )

    st.divider()

    theme_label = "🌙 Switch to Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Switch to Light Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

# ------------------------------------------------------------------------------
# 4. SITE TOP NAVIGATION BAR (PROFESSIONAL HEADER & THEME TOGGLE)
# ------------------------------------------------------------------------------
has_generated = bool(st.session_state["analysis_result"] and st.session_state["draft_response"])

st.markdown(f"""
<div class="app-navbar">
    <div class="nav-brand-group">
        <div class="brand-logo-icon">🛡️</div>
        <div>
            <div class="brand-name">{APP_TITLE}</div>
            <div class="brand-tagline">{APP_TAGLINE}</div>
        </div>
    </div>
    <div class="nav-status-group">
        <div class="system-status-indicator">
            <div class="status-dot"></div>
            <span>Operational · Policy Grounded</span>
        </div>
        <div class="pro-card-badge">
            {st.session_state['theme_mode'].upper()} MODE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. WORKFLOW STEPPER (PROGRESS TRACKER)
# ------------------------------------------------------------------------------
step1_active = "active-step" if not has_generated else ""
step2_active = "active-step" if not has_generated else ""
step3_active = "active-step" if has_generated else ""
step4_active = "active-step" if has_generated else ""

st.markdown(f"""
<div class="workflow-stepper">
    <div class="step-card {step1_active}">
        <div class="step-badge">01</div>
        <div class="step-text">
            <span class="step-title">Intake & Policy</span>
            <span class="step-desc">Grievance & Terms</span>
        </div>
    </div>
    <div class="step-card {step2_active}">
        <div class="step-badge">02</div>
        <div class="step-text">
            <span class="step-title">Tone & Synthesis</span>
            <span class="step-desc">Persona & Generation</span>
        </div>
    </div>
    <div class="step-card {step3_active}">
        <div class="step-badge">03</div>
        <div class="step-text">
            <span class="step-title">Quality Audit</span>
            <span class="step-desc">Policy & False Promise Check</span>
        </div>
    </div>
    <div class="step-card {step4_active}">
        <div class="step-badge">04</div>
        <div class="step-text">
            <span class="step-title">Final Resolution</span>
            <span class="step-desc">Approved & Ready to Send</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. INTAKE WORKSPACE (INTAKE, POLICY, AND TONE CONTROLS)
# ------------------------------------------------------------------------------
col1, col2, col3 = st.columns([1.2, 1.2, 1.0], gap="medium")

with col1:
    st.markdown("""
    <div class="pro-card-header" style="margin-bottom: 8px;">
        <div class="pro-card-title">
            <span>📩</span> Customer Grievance
        </div>
        <span class="pro-card-badge">01 Intake</span>
    </div>
    """, unsafe_allow_html=True)
    complaint_text = st.text_area(
        label="Customer Complaint Input",
        key="complaint_area",
        height=190,
        label_visibility="collapsed",
        placeholder="Paste customer grievance, angry email, or return request here..."
    )
    st.caption(f"📊 Length: **{len(complaint_text)}** characters · **{len(complaint_text.split())}** words")

with col2:
    st.markdown("""
    <div class="pro-card-header" style="margin-bottom: 8px;">
        <div class="pro-card-title">
            <span>📋</span> Policy Guardrails
        </div>
        <span class="pro-card-badge">02 Rules</span>
    </div>
    """, unsafe_allow_html=True)
    policy_text = st.text_area(
        label="Company Policy Input",
        key="policy_area",
        height=190,
        label_visibility="collapsed",
        placeholder="Paste store terms, return policy, warranty guidelines, or refund rules..."
    )
    clause_count = len([line for line in policy_text.splitlines() if line.strip()])
    st.caption(f"🛡️ Guardrails: **{clause_count}** active policy clauses")

with col3:
    st.markdown("""
    <div class="pro-card-header" style="margin-bottom: 8px;">
        <div class="pro-card-title">
            <span>🎭</span> Tone & Action
        </div>
        <span class="pro-card-badge">03 Steering</span>
    </div>
    """, unsafe_allow_html=True)

    current_tone = st.radio(
        label="Response Tone Selector",
        options=["Professional", "Friendly", "Empathetic"],
        index=["Professional", "Friendly", "Empathetic"].index(st.session_state["selected_tone"]),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state["selected_tone"] = current_tone

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    generate_btn = st.button(
        "RESOLVE COMPLAINT →",
        type="primary",
        use_container_width=True,
        help="Analyze complaint, ground against policy, draft response, and validate!"
    )

    clear_btn = st.button("Reset Form ↺", use_container_width=True)
    if clear_btn:
        st.session_state["analysis_result"] = None
        st.session_state["draft_response"] = None
        st.session_state["handoff_data"] = None
        st.rerun()

# ------------------------------------------------------------------------------
# 7. EXECUTION PIPELINE (ANALYSIS + GENERATION + PART 2 QUALITY CHECK)
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
        st.error("⚠️ Please provide customer complaint details before resolving.")
    elif not policy_text.strip():
        st.error("⚠️ Please specify company policy terms for grounding.")
    else:
        with st.spinner("Analyzing complaint intent and checking policy grounding..."):
            try:
                analysis = analyzer.analyze(complaint_text=complaint_text, company_policy=policy_text)
                st.session_state["analysis_result"] = analysis
            except Exception as e:
                st.error(f"❌ Complaint Analysis Failed: {str(e)}")
                st.stop()

        with st.spinner(f"Drafting customer resolution in '{st.session_state['selected_tone']}' tone..."):
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
# 8. OUTPUT BREAKDOWN: COMPLAINT ANALYSIS + QUALITY AUDIT + FINAL WORD
# ------------------------------------------------------------------------------
if st.session_state["analysis_result"] and st.session_state["draft_response"]:
    analysis = st.session_state["analysis_result"]
    draft = st.session_state["draft_response"]
    details = analysis.get("important_details", {})
    grounding = analysis.get("policy_grounding", {})
    missing_info = analysis.get("missing_information", [])

    st.markdown("<hr style='border: 1px solid var(--border-color); margin: 36px 0 24px 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION A: COMPLAINT INTELLIGENCE
    # ==========================================================================
    st.markdown("""
    <div class="pro-card-header">
        <div class="pro-card-title">
            <span>🔍</span> Complaint Intelligence & Triage
        </div>
        <span class="pro-card-badge">Stage 03 · Triage Breakdown</span>
    </div>
    """, unsafe_allow_html=True)

    # 4 Metric Tiles
    m1, m2, m3, m4 = st.columns(4)
    sentiment = analysis.get("sentiment", "Neutral")
    intensity = analysis.get("sentiment_intensity", 5)

    with m1:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-tile-label">Customer Sentiment</div>
            <div class="metric-tile-value">💬 {sentiment} ({intensity}/10)</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-tile-label">Complaint Category</div>
            <div class="metric-tile-value">🏷️ {analysis.get("category", "General")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        order_val = details.get("order_id", "Not provided")
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-tile-label">Order Identifier</div>
            <div class="metric-tile-value">📦 {order_val}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        unsupported = grounding.get("unsupported_demands", [])
        status_txt = "⚠️ Unmet Demands" if unsupported else "✅ Grounded"
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-tile-label">Policy Guardrails</div>
            <div class="metric-tile-value">{status_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    det_col1, det_col2 = st.columns(2, gap="medium")
    with det_col1:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-tile-label">Primary Issue & Sentiment Rationale</div>
            <p style="margin: 4px 0 6px 0; font-weight: 700; font-size: 0.95rem; color: var(--text-primary);">{analysis.get("main_issue", "No summary.")}</p>
            <p style="margin: 0; font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5;">{analysis.get("sentiment_rationale", "")}</p>
        </div>
        """, unsafe_allow_html=True)

    with det_col2:
        declined_str = ", ".join(grounding.get("unsupported_demands", [])) or "None; fully within policy limits"
        approved_str = ", ".join(grounding.get("supported_actions", [])) or "Standard support assistance & verification"
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-tile-label">Policy Rules Applied</div>
            <div style="font-size: 0.86rem; margin-bottom: 6px; color: var(--text-primary);">
                <strong>Declined Demands:</strong> <span style="color: var(--text-secondary);">{declined_str}</span>
            </div>
            <div style="font-size: 0.86rem; color: var(--text-primary);">
                <strong>Approved Actions:</strong> <span style="color: var(--text-secondary);">{approved_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION B: PART 2 QUALITY AUDIT (VEDANT'S AUDITOR MODULE)
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

    with st.spinner("Running Quality Audit (Policy Verification & False Promise Detection)..."):
        audit_res = reviewer.validate_draft(handoff_obj, api_key=review_api_key)

    st.markdown("<hr style='border: 1px solid var(--border-color); margin: 34px 0 24px 0;'>", unsafe_allow_html=True)

    status = audit_res.get("compliance_status", "Non-Compliant")
    chip_class = "chip-compliant" if status == "Compliant" else ("chip-partially" if status == "Partially Compliant" else "chip-noncompliant")
    mode_text = "🤖 Gemini AI Evaluation" if audit_res.get("analysis_mode") == "ai_gemini" else "⚙️ Deterministic Validation Engine"

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em;">
                🛡️ Quality & Compliance Audit
            </div>
            <div class="status-chip {chip_class}">
                {status}
            </div>
        </div>
        <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:var(--text-muted);">{mode_text}</div>
    </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2, gap="medium")
    with q_col1:
        violations = audit_res.get("policy_violations", [])
        fp_data = audit_res.get("false_promises", {})
        fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"

        st.markdown("""
        <div class="metric-tile">
            <div class="metric-tile-label" style="margin-bottom: 8px;">⚖️ Policy Violations & Commitments</div>
        """, unsafe_allow_html=True)

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
                ✅ <strong>Zero policy violations:</strong> Draft conforms to all company terms.
            </div>
            """, unsafe_allow_html=True)

        if fp_detected:
            statements = fp_data.get("suspicious_statements", [])
            for s in statements:
                st.markdown(f"""
                <div class="alert-container-warning">
                    ⚠️ <strong>False Promise Alert:</strong> <em>"{s}"</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-container-success">
                ✅ <strong>No false promises:</strong> Zero unauthorized delivery or refund guarantees.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with q_col2:
        missing = audit_res.get("missing_information", [])
        st.markdown("""
        <div class="metric-tile">
            <div class="metric-tile-label" style="margin-bottom: 8px;">📋 Required Customer Details</div>
        """, unsafe_allow_html=True)

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
                ✅ <strong>All required information requested:</strong> All necessary verification details were requested.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 5 Tone Dimensions
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    scores = audit_res.get("tone_scores", {})
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

    # ==========================================================================
    # SECTION C: FINAL RESOLUTION (CENTERPIECE)
    # ==========================================================================
    st.markdown("<hr style='border: 1px solid var(--border-color); margin: 36px 0 24px 0;'>", unsafe_allow_html=True)

    with st.expander("👁️ Inspect Initial Draft (Raw Part 1 Output)"):
        st.markdown(f"""
        <div class="resolution-body" style="font-size: 0.92rem;">
{draft}
        </div>
        """, unsafe_allow_html=True)

    final_response_text = audit_res.get("improved_response") if status != "Compliant" and audit_res.get("improved_response") else draft

    st.markdown(f"""
    <div class="resolution-card">
        <div class="resolution-header">
            <div style="font-size: 1.15rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                <span>✨</span> Final Approved Resolution
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="status-chip chip-compliant">{st.session_state['selected_tone'].upper()} TONE</span>
                <span class="status-chip chip-compliant">VERIFIED</span>
            </div>
        </div>
        <div class="resolution-body">
{final_response_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Buttons: 1-Click Copy and Re-Draft
    btn_c1, btn_c2 = st.columns([1, 1])
    with btn_c1:
        copy_html = f"""
        <button id="copyFinalBtn" onclick="copyFinalResponse()" style="
            background-color: var(--primary-blue, #1D4ED8);
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 0.92rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s ease;
            width: 100%;
            justify-content: center;
        ">
            <span id="copyIcon">📋</span> <span id="copyText">Copy Final Response</span>
        </button>
        <script>
        function copyFinalResponse() {{
            const text = {json.dumps(final_response_text)};
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copyFinalBtn');
                const icon = document.getElementById('copyIcon');
                const label = document.getElementById('copyText');
                btn.style.backgroundColor = '#059669';
                icon.innerText = '✅';
                label.innerText = 'Copied to Clipboard!';
                setTimeout(() => {{
                    btn.style.backgroundColor = '#1D4ED8';
                    icon.innerText = '📋';
                    label.innerText = 'Copy Final Response';
                }}, 2500);
            }}).catch(err => console.error(err));
        }}
        </script>
        """
        components.html(copy_html, height=54)

    with btn_c2:
        if st.button(f"🔄 Re-Draft in '{st.session_state['selected_tone']}' Tone", use_container_width=True):
            with st.spinner("Re-drafting response..."):
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

    # Expandable Prompt Lab & Audit Payload
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("🛠️ Prompt Engineering Lab & System Telemetry"):
        st.markdown("##### 1. Core System Prompt & Grounding Directives")
        st.code(CORE_SYSTEM_PROMPT, language="markdown")

        st.markdown("##### 2. Complaint Analysis Prompt Template")
        st.code(ANALYSIS_USER_PROMPT, language="markdown")

        st.markdown(f"##### 3. Tone Steering Directive Applied ({st.session_state['selected_tone']})")
        st.code(TONE_DIRECTIVES.get(st.session_state["selected_tone"], ""), language="markdown")

        st.markdown("##### 4. Response Generation Prompt Template")
        st.code(RESPONSE_USER_PROMPT, language="markdown")

        st.markdown("##### 5. Complete Quality Audit JSON Payload")
        st.json(audit_res)

# ------------------------------------------------------------------------------
# 9. PROFESSIONAL FOOTER
# ------------------------------------------------------------------------------
st.markdown(f"""
<div class="pro-footer">
    <div class="pro-footer-brand">
        <span>🛡️</span> {APP_TITLE} · Customer Complaint Resolution Assistant
    </div>
    <div class="pro-footer-meta">
        Policy Grounded · Zero False Promises · 2026 Enterprise Edition
    </div>
</div>
""", unsafe_allow_html=True)
