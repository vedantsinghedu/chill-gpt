"""
ChillGPT – Customer Support Response Assistant
==============================================================================
College Prompt Engineering Project
Part 1: Complaint Analysis & Response Generation Module

Stack: Python 3.10+ | Streamlit | Prompt Engineering
Authors: College Team (Part 1 Owner)
==============================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Dict, Any

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    MODULE_TITLE,
    APP_ICON,
    CUSTOM_CSS,
    load_sample_policies,
    load_sample_complaints
)
from modules.llm_client import LLMClient
from modules.analyzer import ComplaintAnalyzer
from modules.generator import ResponseGenerator
from modules.reviewer_interface import create_handoff_package
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
    page_title=f"{APP_TITLE} - {MODULE_TITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom Styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. SESSION STATE & DATA INITIALIZATION
# ------------------------------------------------------------------------------
sample_policies = load_sample_policies()
sample_complaints = load_sample_complaints()

default_policy = sample_policies[0]["text"] if sample_policies else ""
default_complaint = sample_complaints[0]["text"] if sample_complaints else ""

# Ensure keys for input widgets exist in session_state
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
# 3. SIDEBAR CONFIGURATION & LLM SETTINGS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### {APP_ICON} **ChillGPT Settings**")
    st.caption("Prompt Engineering & LLM Engine Setup")

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
        model_name = st.selectbox("Gemini Model", ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"])
        provider_slug = "gemini"
    elif provider_option == "OpenAI / Compatible":
        api_key = st.text_input("API Key", type="password", help="OpenAI or custom provider key.")
        model_name = st.text_input("Model Name", value="gpt-4o-mini", help="E.g. gpt-4o-mini, llama-3.3-70b-versatile, etc.")
        base_url = st.text_input("Custom Base URL (Optional)", value="", placeholder="https://api.groq.com/openai/v1")
        provider_slug = "openai"
    else:
        provider_slug = "simulator"
        st.success("✅ Offline Prompt Simulator Active: Fast, zero-cost, and reliable for college grading.")

    st.divider()

    # Pre-Loaded Test Scenarios
    st.markdown("### 📋 **Quick Test Scenarios**")
    st.caption("Load realistic test cases with 1 click:")

    scenario_titles = [c["title"] for c in sample_complaints]
    selected_scenario_title = st.selectbox("Choose a test scenario:", scenario_titles, key="scenario_selector")

    if st.button("📥 Load Selected Scenario", use_container_width=True):
        matched_complaint = next((c for c in sample_complaints if c["title"] == selected_scenario_title), None)
        if matched_complaint:
            st.session_state["complaint_area"] = matched_complaint["text"]
            # Match policy
            policy_id = matched_complaint.get("policy_id")
            matched_policy = next((p for p in sample_policies if p["id"] == policy_id), None)
            if matched_policy:
                st.session_state["policy_area"] = matched_policy["text"]

            # Clear previous results for fresh execution
            st.session_state["analysis_result"] = None
            st.session_state["draft_response"] = None
            st.session_state["handoff_data"] = None
            st.rerun()

    st.divider()

    temperature = st.slider(
        "Temperature (Grounding Control)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values (0.1 - 0.3) enforce strict factual grounding and policy adherence."
    )

    st.divider()
    st.markdown("### ℹ️ **Project Information**")
    st.caption("**Course**: Prompt Engineering")
    st.caption("**Scope**: Part 1 (Complaint Analysis & Response Generation)")
    st.caption("**Teammate Integration**: Part 2 Review & Validation Module will ingest the exported handoff state.")

# ------------------------------------------------------------------------------
# 4. MAIN APPLICATION HEADER
# ------------------------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <div style="margin-bottom: 8px;">
        <span class="badge-pill badge-project">College Prompt Engineering Project</span>
        <span class="badge-pill badge-part1">Part 1: Active Module</span>
    </div>
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>{APP_SUBTITLE} &mdash; <strong>{MODULE_TITLE}</strong></p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. INPUT SECTION: COMPLAINT & COMPANY POLICY
# ------------------------------------------------------------------------------
col_comp, col_pol = st.columns([1, 1], gap="medium")

with col_comp:
    st.markdown("#### 1️⃣ Customer Complaint")
    st.caption("Paste or edit the incoming customer complaint message:")
    complaint_text = st.text_area(
        label="Customer Complaint Input",
        key="complaint_area",
        height=260,
        label_visibility="collapsed",
        placeholder="Enter customer complaint details here..."
    )
    st.caption(f"📝 Length: **{len(complaint_text)}** characters | **{len(complaint_text.split())}** words")

with col_pol:
    st.markdown("#### 2️⃣ Company Policy & Grounding Rules")
    st.caption("The response MUST strictly adhere to this policy (no unauthorized promises):")
    policy_text = st.text_area(
        label="Company Policy Input",
        key="policy_area",
        height=260,
        label_visibility="collapsed",
        placeholder="Paste company terms, return policies, warranty rules, SLA, etc..."
    )
    st.caption(f"🛡️ Guardrails: Policy contains **{len(policy_text.splitlines())}** policy sections.")

# ------------------------------------------------------------------------------
# 6. TONE SELECTION & ACTION CONTROLS
# ------------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

tone_col, btn_col1, btn_col2 = st.columns([2, 1.5, 1], gap="medium")

with tone_col:
    st.markdown("**🎭 Select Response Tone:**")
    current_tone = st.radio(
        label="Response Tone Selector",
        options=["Professional", "Friendly", "Empathetic"],
        index=["Professional", "Friendly", "Empathetic"].index(st.session_state["selected_tone"]),
        horizontal=True,
        label_visibility="collapsed",
        help="Select the tone style for the generated customer support response."
    )
    st.session_state["selected_tone"] = current_tone

with btn_col1:
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button(
        "🚀 Generate Response",
        type="primary",
        use_container_width=True,
        help="Analyzes the complaint and drafts a policy-grounded customer response in the selected tone."
    )

with btn_col2:
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    clear_btn = st.button("🧹 Clear", use_container_width=True)
    if clear_btn:
        st.session_state["analysis_result"] = None
        st.session_state["draft_response"] = None
        st.session_state["handoff_data"] = None
        st.rerun()

# ------------------------------------------------------------------------------
# 7. EXECUTION PIPELINE (ANALYSIS + GENERATION + HANDOFF CREATION)
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
        st.error("⚠️ Please enter a customer complaint before generating a response.")
    elif not policy_text.strip():
        st.error("⚠️ Please provide a company policy for grounding before generating a response.")
    else:
        with st.spinner("🔍 Analyzing complaint (identifying sentiment, category, details, and missing info)..."):
            try:
                analysis = analyzer.analyze(complaint_text=complaint_text, company_policy=policy_text)
                st.session_state["analysis_result"] = analysis
            except Exception as e:
                st.error(f"❌ Complaint Analysis Failed: {str(e)}")
                st.stop()

        with st.spinner(f"✍️ Generating customer support response ({st.session_state['selected_tone']} tone)..."):
            try:
                draft = generator.generate_response(
                    complaint_text=complaint_text,
                    company_policy=policy_text,
                    analysis_data=st.session_state["analysis_result"],
                    tone=st.session_state["selected_tone"],
                    temperature=temperature
                )
                st.session_state["draft_response"] = draft

                # Package official handoff for Part 2 Teammate
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
# 8. OUTPUT DISPLAY: SEPARATE CLEAN SECTIONS
# ------------------------------------------------------------------------------
if st.session_state["analysis_result"] and st.session_state["draft_response"]:
    analysis = st.session_state["analysis_result"]
    draft = st.session_state["draft_response"]
    details = analysis.get("important_details", {})
    grounding = analysis.get("policy_grounding", {})
    missing_info = analysis.get("missing_information", [])

    st.markdown("<hr style='margin: 35px 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 1: COMPLAINT ANALYSIS DASHBOARD
    # ==========================================================================
    st.markdown("### 📊 **Section 1: Complaint Analysis**")
    st.caption("Extracted using structured prompt engineering with strict policy grounding:")

    # 4 Key Metric Cards
    m1, m2, m3, m4 = st.columns(4)

    sentiment = analysis.get("sentiment", "Neutral")
    intensity = analysis.get("sentiment_intensity", 5)
    sentiment_css_class = f"sentiment-{sentiment.lower()}" if sentiment.lower() in ["angry", "frustrated", "anxious", "disappointed", "neutral"] else "sentiment-neutral"

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Customer Sentiment</div>
            <div class="metric-value"><span class="{sentiment_css_class}">{sentiment} ({intensity}/10)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Complaint Category</div>
            <div class="metric-value">🏷️ {analysis.get("category", "General")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Order / Customer ID</div>
            <div class="metric-value">📦 {details.get("order_id", "Not provided")}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        unsupported = grounding.get("unsupported_demands", [])
        status_text = "⚠️ Out-of-Policy Demands" if unsupported else "✅ Within Policy"
        status_color = "#DC2626" if unsupported else "#16A34A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Policy Grounding Check</div>
            <div class="metric-value" style="color: {status_color}; font-size: 1.05rem;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Analysis Columns
    det_col1, det_col2 = st.columns([1, 1], gap="medium")

    with det_col1:
        st.markdown("##### 🎯 Main Issue")
        st.info(analysis.get("main_issue", "No summary provided."))

        st.markdown("##### 🧠 Sentiment Rationale")
        st.write(analysis.get("sentiment_rationale", "No rationale available."))

        st.markdown("##### 📌 Key Details Extracted")
        st.markdown(f"""
        - **Customer Name**: `{details.get('customer_name', 'Not provided')}`
        - **Product / Service**: `{details.get('product_name', 'Not provided')}`
        - **Timeline Mentioned**: `{details.get('dates_mentioned', 'Not provided')}`
        - **Specific Demands**: `{", ".join(details.get('demands_made', [])) or 'None'}`
        """)

    with det_col2:
        # Missing Information Alert
        if missing_info:
            st.markdown("##### ⚠️ Missing Information (Action Required)")
            for item in missing_info:
                st.warning(f"**Missing from Complaint**: {item}")
        else:
            st.markdown("##### ✅ Missing Information Check")
            st.success("All necessary details and identifiers provided.")

        st.markdown("##### 🛡️ Policy Grounding & Guardrails")
        st.markdown("**Disallowed / Unsupported Demands** *(Declined courteously)*:")
        if grounding.get("unsupported_demands"):
            for und in grounding["unsupported_demands"]:
                st.markdown(f"- ❌ **Declined**: {und}")
        else:
            st.markdown("- *None; customer request fits within policy.*")

        st.markdown("**Approved / Supported Actions** *(Offered to customer)*:")
        if grounding.get("supported_actions"):
            for sup in grounding["supported_actions"]:
                st.markdown(f"- ✅ **Approved**: {sup}")
        else:
            st.markdown("- *Standard customer service communication.*")

        st.caption(f"📜 **Applicable Clause(s)**: {grounding.get('applicable_clauses', 'General')}")

    st.markdown("<hr style='margin: 35px 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 2: GENERATED CUSTOMER SUPPORT RESPONSE
    # ==========================================================================
    st.markdown("### ✉️ **Section 2: Generated Customer Support Response**")
    
    resp_header_col1, resp_header_col2 = st.columns([3, 1])
    with resp_header_col1:
        st.caption(f"Tone applied: **{st.session_state['selected_tone']}** &bull; Grounded strictly against policy rules &bull; Never promises unauthorized refunds or replacements.")
    with resp_header_col2:
        # Quick re-draft button if user changes tone
        if st.button(f"🔄 Re-Draft in '{st.session_state['selected_tone']}'", use_container_width=True):
            with st.spinner(f"Re-drafting response in '{st.session_state['selected_tone']}' tone..."):
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

    # Styled Response Text Container
    st.markdown(f"""
    <div class="response-container">
{draft}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Requirement 7: Dedicated Copy Button (Interactive HTML/JS with Visual Feedback)
    copy_html = f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <button id="copyBtn" onclick="copyToClipboard()" style="
            background-color: #0284C7;
            color: #FFFFFF;
            border: none;
            padding: 9px 18px;
            border-radius: 8px;
            font-size: 0.92rem;
            font-weight: 600;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            transition: all 0.2s ease;
        ">
            <span id="copyIcon">📋</span> <span id="copyText">Copy Generated Response</span>
        </button>
    </div>
    <script>
    function copyToClipboard() {{
        const textToCopy = {json.dumps(draft)};
        navigator.clipboard.writeText(textToCopy).then(() => {{
            const btn = document.getElementById('copyBtn');
            const icon = document.getElementById('copyIcon');
            const label = document.getElementById('copyText');
            btn.style.backgroundColor = '#16A34A';
            icon.innerText = '✅';
            label.innerText = 'Copied to Clipboard!';
            setTimeout(() => {{
                btn.style.backgroundColor = '#0284C7';
                icon.innerText = '📋';
                label.innerText = 'Copy Generated Response';
            }}, 2500);
        }}).catch(err => {{
            console.error('Copy failed: ', err);
        }});
    }}
    </script>
    """
    components.html(copy_html, height=45)

    with st.expander("📄 View Response in Raw / Selectable Format"):
        st.code(draft, language=None)

    st.markdown("<hr style='margin: 35px 0;'>", unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 3: TEAMMATE INTEGRATION HOOK (PART 2 HANDOFF)
    # ==========================================================================
    st.markdown("### 🤝 **Section 3: Teammate Handoff (Part 2: Review & Validation)**")
    st.markdown(f"""
    <div class="handoff-box">
        <div class="handoff-title">📦 Data Package Ready for Teammate Module</div>
        <p style="margin: 0; color: #166534; font-size: 0.9rem;">
            Part 1 execution is complete. The structured complaint analysis and generated draft response
            have been packaged into <code>st.session_state["handoff_data"]</code>. Your teammate can now
            seamlessly ingest this state to implement their Review & Validation rules!
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("👁️ View Handoff Data Contract (JSON Payload for Part 2)"):
        st.caption("Standardized schema created by Part 1:")
        st.json(st.session_state["handoff_data"])

    # ==========================================================================
    # SECTION 4: PROMPT ENGINEERING INSPECTOR (ACADEMIC EVALUATION)
    # ==========================================================================
    with st.expander("🔍 **Section 4: Prompt Engineering Inspector (Grading Details)**"):
        st.markdown("##### 1. System Prompt & Grounding Guardrails")
        st.code(CORE_SYSTEM_PROMPT, language="markdown")

        st.markdown("##### 2. Complaint Analysis Prompt Template")
        st.code(ANALYSIS_USER_PROMPT, language="markdown")

        st.markdown(f"##### 3. Tone Steering Directive Applied ({st.session_state['selected_tone']})")
        st.code(TONE_DIRECTIVES.get(st.session_state["selected_tone"], ""), language="markdown")

        st.markdown("##### 4. Response Generation Prompt Template")
        st.code(RESPONSE_USER_PROMPT, language="markdown")

# ------------------------------------------------------------------------------
# 9. FOOTER
# ------------------------------------------------------------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption(f"**ChillGPT** &mdash; College Prompt Engineering Project | Part 1: Complaint Analysis & Response Generation | Ready for Part 2 Teammate Integration")
