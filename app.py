"""
ChillGPT – Customer Support Response Assistant
Visual Identity: Neo-Minimalist Editorial & Pop Yellow Design
Inspired by Wave AI / Rabbit r1 / Modern Japanese & Swiss Studio Aesthetic
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
# 3. SIDEBAR CONFIGURATION (MINIMALIST, SLEEK)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid var(--border-subtle); margin-bottom: 16px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 900; letter-spacing: -0.02em;">
            ⚡ STUDIO CONTROLS
        </div>
        <div style="font-family: 'Space Mono', monospace; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">
            Engine & Scenarios
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
        st.caption("⚡ Offline Simulator: Fast, deterministic, and free.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Pre-Loaded Test Scenarios
    st.markdown("##### 📋 Load Test Scenario")
    scenario_titles = [c["title"] for c in sample_complaints]
    selected_scenario_title = st.selectbox("Select scenario:", scenario_titles, key="scenario_selector", label_visibility="collapsed")

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
        "Temperature (Grounding Control)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values enforce strict factual grounding and policy adherence."
    )

    st.divider()
    theme_label = "🌙 Dark Mode" if st.session_state["theme_mode"] == "light" else "☀️ Light Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state["theme_mode"] = "dark" if st.session_state["theme_mode"] == "light" else "light"
        st.rerun()

# ------------------------------------------------------------------------------
# 4. SITE TOP NAVIGATION BAR (Matches video frame 00:00)
# ------------------------------------------------------------------------------
st.markdown("""
<div class="site-nav">
    <div class="nav-brand">CHILLGPT ✦</div>
    <div class="nav-links">
        <span class="nav-link-item">[ THE SITUATION ]</span>
        <span class="nav-link-item">[ POLICY RULES ]</span>
        <span class="nav-link-item">[ QUALITY AUDIT ]</span>
        <span class="nav-link-item">[ THE FINAL WORD ]</span>
    </div>
    <div>
        <span class="nav-pill-badge">AI COPILOT</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. GIANT TYPOGRAPHY & HERO POP-YELLOW CONTAINER (Matches frame 00:00 - 00:02)
# ------------------------------------------------------------------------------
st.markdown("""
<div class="giant-bg-word">CHILLGPT</div>

<div class="hero-yellow-container">
    <div class="hero-content-grid">
        <div class="hero-left-desc">
            ✦ A.I. ENGINE DETECTS CUSTOMER GRIEVANCES BEFORE THEY ESCALATE — 100% POLICY GROUNDED.
            <br><br>
            <div style="font-size: 1.5rem;">✿ ⚡ 🌼</div>
        </div>
        <div class="phone-mockup-wrap">
            <div class="phone-device">
                <div class="phone-notch"></div>
                <div class="phone-inner-screen">
                    <div style="font-family:'Space Mono', monospace; font-size:0.65rem; font-weight:700; text-transform:uppercase; margin-bottom: 2px;">
                        CHILLGPT
                    </div>
                    <div class="phone-mascot-face">🐰</div>
                    <div class="phone-app-pill">AI ASSISTANT</div>
                </div>
            </div>
        </div>
        <div class="hero-right-meta">
            | REAL-TIME POLICY AUDIT |<br>
            | ZERO FALSE PROMISES |<br>
            | MULTI-TONE STEERING |<br>
            | 100% GROUNDED RESPONSES |
        </div>
    </div>
</div>

<div class="ticker-wrap">
    <span>[ COMPLAINT ANALYSIS ]</span>
    <span>✦</span>
    <span>[ POLICY GROUNDING ]</span>
    <span>✦</span>
    <span>[ FALSE PROMISE SHIELD ]</span>
    <span>✦</span>
    <span>[ TONE OPTIMIZER ]</span>
    <span>✦</span>
    <span>[ 100% VERIFIED ]</span>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. EDITORIAL WORKSPACE CARDS: 01, 02, 03 (Matches frame 00:13 - 00:15)
# ------------------------------------------------------------------------------
c1, c2, c3 = st.columns([1.2, 1.2, 1], gap="medium")

with c1:
    st.markdown("""
    <div class="editorial-card">
        <div>
            <div class="card-big-num">01</div>
            <div class="card-header-label">THE SITUATION</div>
            <div class="card-sub-desc">Customer grievance, angry email, or return inquiry.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    complaint_text = st.text_area(
        label="Customer Complaint Input",
        key="complaint_area",
        height=200,
        label_visibility="collapsed",
        placeholder="Paste customer grievance, angry email, or return request here..."
    )
    st.caption(f"📝 Length: **{len(complaint_text)}** chars | **{len(complaint_text.split())}** words")

with c2:
    st.markdown("""
    <div class="editorial-card">
        <div>
            <div class="card-big-num">02</div>
            <div class="card-header-label">THE RULES</div>
            <div class="card-sub-desc">Company terms, return windows, warranty & refund limits.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    policy_text = st.text_area(
        label="Company Policy Input",
        key="policy_area",
        height=200,
        label_visibility="collapsed",
        placeholder="Paste store terms, return policy, warranty guidelines, or refund rules..."
    )
    st.caption(f"🛡️ Guardrails: **{len(policy_text.splitlines())}** policy clauses active")

with c3:
    st.markdown("""
    <div class="editorial-card">
        <div>
            <div class="card-big-num">03</div>
            <div class="card-header-label">THE VIBE & ACTION</div>
            <div class="card-sub-desc">Select response tone and run full generation & audit.</div>
        </div>
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

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button(
        "MAKE IT CHILL ✦",
        type="primary",
        use_container_width=True,
        help="Analyze complaint, ground against policy, draft response, and validate!"
    )

    clear_btn = st.button("RESET ↺", use_container_width=True)
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
# 8. OUTPUT BREAKDOWN: COMPLAINT ANALYSIS + QUALITY AUDIT + FINAL WORD
# ------------------------------------------------------------------------------
if st.session_state["analysis_result"] and st.session_state["draft_response"]:
    analysis = st.session_state["analysis_result"]
    draft = st.session_state["draft_response"]
    details = analysis.get("important_details", {})
    grounding = analysis.get("policy_grounding", {})
    missing_info = analysis.get("missing_information", [])

    st.markdown("<hr style='border: 1px solid var(--border-subtle); margin: 40px 0 28px 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION A: THE BREAKDOWN (ANALYSIS)
    # ==========================================================================
    st.markdown("""
    <div style="font-family:'Space Grotesk', sans-serif; font-size:1.4rem; font-weight:900; margin-bottom:14px; letter-spacing:-0.03em;">
        04 — THE BREAKDOWN ✦ COMPLAINT INTELLIGENCE
    </div>
    """, unsafe_allow_html=True)

    # 4 Metric Capsules
    m1, m2, m3, m4 = st.columns(4)
    sentiment = analysis.get("sentiment", "Neutral")
    intensity = analysis.get("sentiment_intensity", 5)

    with m1:
        st.markdown(f"""
        <div class="metric-capsule">
            <div class="metric-capsule-lbl">Customer Sentiment</div>
            <div class="metric-capsule-val">⚡ {sentiment} ({intensity}/10)</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-capsule">
            <div class="metric-capsule-lbl">Complaint Category</div>
            <div class="metric-capsule-val">🏷️ {analysis.get("category", "General")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-capsule">
            <div class="metric-capsule-lbl">Order Identifier</div>
            <div class="metric-capsule-val">📦 {details.get("order_id", "Not provided")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        unsupported = grounding.get("unsupported_demands", [])
        status_txt = "⚠️ Out-of-Policy" if unsupported else "✅ Grounded"
        st.markdown(f"""
        <div class="metric-capsule">
            <div class="metric-capsule-lbl">Policy Guardrails</div>
            <div class="metric-capsule-val">{status_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    det_col1, det_col2 = st.columns(2, gap="medium")
    with det_col1:
        st.markdown(f"""
        <div class="metric-capsule">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:0.95rem; margin-bottom:6px;">
                🎯 MAIN ISSUE & SENTIMENT RATIONALE
            </div>
            <p style="margin: 0 0 8px 0; font-weight: 600; font-size: 0.95rem;">{analysis.get("main_issue", "No summary.")}</p>
            <p style="margin: 0; font-size: 0.85rem; color: var(--text-secondary);">{analysis.get("sentiment_rationale", "")}</p>
        </div>
        """, unsafe_allow_html=True)

    with det_col2:
        st.markdown(f"""
        <div class="metric-capsule">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:0.95rem; margin-bottom:6px;">
                🛡️ GROUNDING RULES APPLIED
            </div>
            <div style="font-size: 0.85rem; margin-bottom: 4px;">
                <strong>Declined:</strong> {", ".join(grounding.get("unsupported_demands", [])) or "None; fits within policy"}
            </div>
            <div style="font-size: 0.85rem;">
                <strong>Approved Actions:</strong> {", ".join(grounding.get("supported_actions", [])) or "Standard support assistance"}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION B: PART 2 QUALITY AUDIT (THE QUALITY CHECK)
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

    with st.spinner("⚡ Running Quality Audit (Part 2 Policy Verification)..."):
        audit_res = reviewer.validate_draft(handoff_obj, api_key=review_api_key)

    st.markdown("<hr style='border: 1px solid var(--border-subtle); margin: 34px 0 24px 0;'>", unsafe_allow_html=True)

    status = audit_res.get("compliance_status", "Non-Compliant")
    pill_cls = "status-compliant" if status == "Compliant" else ("status-partially" if status == "Partially Compliant" else "status-noncompliant")
    mode_text = "🤖 Gemini AI Evaluation" if audit_res.get("analysis_mode") == "ai_gemini" else "⚙️ Deterministic Engine"

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-size:1.4rem; font-weight:900; letter-spacing:-0.03em;">
                05 — QUALITY AUDIT ✦ POLICY VERIFICATION
            </div>
            <div class="status-pill {pill_cls}">
                {status}
            </div>
        </div>
        <div style="font-family:'Space Mono', monospace; font-size:0.75rem; color:var(--text-muted);">{mode_text}</div>
    </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2, gap="medium")
    with q_col1:
        violations = audit_res.get("policy_violations", [])
        fp_data = audit_res.get("false_promises", {})
        fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"

        st.markdown("""
        <div class="metric-capsule">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:0.95rem; margin-bottom:8px;">
                ⚖️ POLICY VIOLATIONS & FALSE PROMISES
            </div>
        """, unsafe_allow_html=True)

        if violations:
            for v in violations:
                st.markdown(f"- ❌ **Violation**: {v}")
        else:
            st.markdown("✅ **Zero policy violations** detected in the response.")

        if fp_detected:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            st.markdown("⚠️ **False Promise Alert:**")
            for s in fp_data.get("suspicious_statements", []):
                st.markdown(f"> *\"{s}\"*")
        else:
            st.markdown("✅ **No unauthorized commitments or false promises.**")
        st.markdown("</div>", unsafe_allow_html=True)

    with q_col2:
        missing = audit_res.get("missing_information", [])
        st.markdown("""
        <div class="metric-capsule">
            <div style="font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:0.95rem; margin-bottom:8px;">
                📋 REQUIRED INFORMATION AUDIT
            </div>
        """, unsafe_allow_html=True)

        if missing:
            for idx, item in enumerate(missing, 1):
                st.markdown(f"**{idx}. {item.get('item', 'Item')}** — *{item.get('reason', '')}*")
        else:
            st.markdown("✅ All necessary customer details requested.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 5 Tone Dimensions
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
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
            <div class="metric-capsule" style="text-align: center; padding: 12px;">
                <div style="font-family:'Space Grotesk', sans-serif; font-size:1.35rem; font-weight:900;">{val}/10</div>
                <div style="font-family:'Space Mono', monospace; font-size:0.68rem; text-transform:uppercase; color:var(--text-muted);">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(max(0.0, min(1.0, val / 10.0)))

    # ==========================================================================
    # SECTION C: THE FINAL WORD ✦ READY TO SEND (CENTERPIECE)
    # ==========================================================================
    st.markdown("<hr style='border: 1px solid var(--border-subtle); margin: 36px 0 24px 0;'>", unsafe_allow_html=True)

    with st.expander("👁️ View Original Draft (Part 1 Initial Generation)"):
        st.markdown(f"""
        <div class="metric-capsule" style="white-space: pre-wrap; font-size: 0.92rem; line-height: 1.6;">
{draft}
        </div>
        """, unsafe_allow_html=True)

    final_response_text = audit_res.get("improved_response") if status != "Compliant" and audit_res.get("improved_response") else draft

    st.markdown(f"""
    <div class="showcase-container">
        <div class="showcase-header">
            <div class="showcase-title">
                <span>⚡</span> THE FINAL WORD ✦ READY TO SEND
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="status-pill status-compliant">{st.session_state['selected_tone']} TONE</span>
                <span class="status-pill status-compliant">VERIFIED</span>
            </div>
        </div>
        <div class="showcase-bubble">
{final_response_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Copy Button
    btn_c1, btn_c2 = st.columns([1, 1])
    with btn_c1:
        copy_html = f"""
        <button id="copyFinalBtn" onclick="copyFinalResponse()" style="
            background-color: #000000;
            color: #FFFFFF;
            border: none;
            border-radius: 999px;
            padding: 12px 28px;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.95rem;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s ease;
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
                btn.style.backgroundColor = '#16A34A';
                icon.innerText = '✅';
                label.innerText = 'COPIED TO CLIPBOARD!';
                setTimeout(() => {{
                    btn.style.backgroundColor = '#000000';
                    icon.innerText = '📋';
                    label.innerText = 'COPY FINAL RESPONSE';
                }}, 2500);
            }}).catch(err => console.error(err));
        }}
        </script>
        """
        components.html(copy_html, height=52)

    with btn_c2:
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

    # Expandable Prompt Lab
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("[ ✦ BEHIND THE RESPONSE — PROMPT LAB ]"):
        st.markdown("##### 1. System Prompt & Grounding Guardrails")
        st.code(CORE_SYSTEM_PROMPT, language="markdown")

        st.markdown("##### 2. Complaint Analysis Prompt Template")
        st.code(ANALYSIS_USER_PROMPT, language="markdown")

        st.markdown(f"##### 3. Tone Steering Directive Applied ({st.session_state['selected_tone']})")
        st.code(TONE_DIRECTIVES.get(st.session_state["selected_tone"], ""), language="markdown")

        st.markdown("##### 4. Response Generation Prompt Template")
        st.code(RESPONSE_USER_PROMPT, language="markdown")

        st.markdown("##### 5. Quality Audit JSON Output")
        st.json(audit_res)

# ------------------------------------------------------------------------------
# 9. GIANT ARCHITECTURAL FOOTER WORDMARK (Matches frame 00:16 WAVEAI)
# ------------------------------------------------------------------------------
st.markdown("""
<div class="footer-giant-wordmark">CHILLGPT</div>
<div class="footer-meta-line">
    <span>WE ARE A GLOBAL AI ENGINE TO RESOLVE COMPLAINTS BEFORE THEY ESCALATE</span>
    <span>| CHILLGPT COPILOT | 2026 |</span>
</div>
""", unsafe_allow_html=True)
