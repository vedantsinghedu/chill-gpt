"""
ChillGPT — Customer Support Response Assistant
Part 2: Response Review and Policy Validation Module
Standalone Testing and Integration Interface
Author: Member 2 (Vedant)
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Add current directory and parent directory to sys.path so modules can be imported directly
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from modules.response_reviewer import review_response

# Page Configuration
st.set_page_config(
    page_title="ChillGPT — Response Reviewer & Policy Validator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS-Style Styling (Blue & White Palette)
st.markdown("""
<style>
    /* Global Typography & Palette */
    :root {
        --primary-blue: #1E40AF;
        --secondary-blue: #2563EB;
        --light-blue: #EFF6FF;
        --slate-bg: #F8FAFC;
        --card-border: #E2E8F0;
        --text-dark: #0F172A;
        --text-muted: #64748B;
        --success: #16A34A;
        --warning: #D97706;
        --danger: #DC2626;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* Header Styling */
    .saas-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .saas-header h1 {
        color: #FFFFFF !important;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
        letter-spacing: -0.02em;
    }
    .saas-header p {
        color: #DBEAFE;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Card Containers */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid var(--card-border);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .saas-card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-compliant {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .badge-partially {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
    }
    .badge-noncompliant {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }
    .badge-info {
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
    }

    /* Metric Cards */
    .metric-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E40AF;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* Alert Boxes */
    .alert-danger-box {
        background: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        color: #991B1B;
        margin-bottom: 10px;
    }
    .alert-warning-box {
        background: #FFFBEB;
        border-left: 4px solid #D97706;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        color: #92400E;
        margin-bottom: 10px;
    }
    .alert-success-box {
        background: #F0FDF4;
        border-left: 4px solid #16A34A;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        color: #166534;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Preset Scenarios for Rapid Testing
PRESETS = {
    "Custom / Blank": {
        "complaint": "",
        "policy": "",
        "response": ""
    },
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
    st.markdown("### ⚙️ System Settings")
    api_key_env = os.environ.get("GEMINI_API_KEY", "").strip()
    user_api_key = st.text_input(
        "Gemini API Key (Optional)",
        value=api_key_env,
        type="password",
        help="Leave empty to run in Deterministic Local Validation Mode."
    )

    if user_api_key:
        st.success("🟢 API Key Configured (AI Mode Active)")
    else:
        st.info("🔵 Deterministic Local Mode (No Key Needed)")

    st.markdown("---")
    st.markdown("### 📋 Load Test Scenario")
    selected_scenario = st.selectbox(
        "Select a pre-configured test case:",
        options=list(PRESETS.keys()),
        index=1
    )

    st.markdown("---")
    st.markdown("### 📌 Module Details")
    st.caption("**Project**: ChillGPT Mini-Project")
    st.caption("**Module**: Part 2 - Response Review & Policy Validation")
    st.caption("**Developer**: Member 2 (Vedant)")
    st.caption("**Integration**: Independent module ready for Part 1 handoff.")

# Header
st.markdown("""
<div class="saas-header">
    <h1>ChillGPT — Response Review & Policy Validator</h1>
    <p>Part 2 Quality Assurance Engine: Auditing customer support responses for policy compliance, false promises, missing verification data, and tone excellence.</p>
</div>
""", unsafe_allow_html=True)

# Preset Data Handling
preset_data = PRESETS[selected_scenario]

# Input Columns
col_in1, col_in2 = st.columns([1, 1], gap="medium")

with col_in1:
    st.markdown("##### 1. Customer Complaint")
    complaint_input = st.text_area(
        "Enter the customer's grievance message:",
        value=preset_data["complaint"],
        height=140,
        placeholder="e.g. My order arrived broken and I want my money back...",
        key="complaint_input"
    )

    st.markdown("##### 2. Company Policy")
    policy_input = st.text_area(
        "Enter relevant company policy terms:",
        value=preset_data["policy"],
        height=140,
        placeholder="e.g. Items can be returned within 7 days with photo proof. No instant refunds...",
        key="policy_input"
    )

with col_in2:
    st.markdown("##### 3. AI-Generated Response (from Part 1)")
    response_input = st.text_area(
        "Enter the generated response to audit:",
        value=preset_data["response"],
        height=322,
        placeholder="e.g. Hello! We are refunding your money right away...",
        key="response_input"
    )

# Action Button
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    review_clicked = st.button("🔍 Review and Validate Response", type="primary", use_container_width=True)

# Evaluation Logic
if review_clicked or "review_results" in st.session_state:
    if review_clicked:
        with st.spinner("Auditing response compliance and evaluating tone..."):
            results = review_response(
                customer_complaint=complaint_input,
                company_policy=policy_input,
                generated_response=response_input,
                api_key=user_api_key if user_api_key else None
            )
            st.session_state["review_results"] = results
    else:
        results = st.session_state["review_results"]

    st.markdown("---")
    st.markdown("### 📊 Response Review Dashboard")

    # Overview Banner: Status Badges & Analysis Mode
    status = results.get("compliance_status", "Non-Compliant")
    badge_class = {
        "Compliant": "badge-compliant",
        "Partially Compliant": "badge-partially",
        "Non-Compliant": "badge-noncompliant"
    }.get(status, "badge-noncompliant")

    mode = results.get("analysis_mode", "deterministic_fallback")
    mode_label = "🤖 Gemini AI Evaluation" if mode == "ai_gemini" else "⚙️ Deterministic Local Validation Engine"

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px 20px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-weight: 600; color: #0F172A;">Compliance Status:</span>
            <span class="badge {badge_class}">{status}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="badge badge-info">{mode_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4-Column Audit Results
    tab_overview, tab_tone, tab_improved, tab_json = st.tabs([
        "🛡️ Policy & Promise Audit",
        "🎭 Tone & Professionalism",
        "✨ Final Improved Response",
        "🔍 Structured JSON Payload"
    ])

    with tab_overview:
        res_col1, res_col2 = st.columns(2, gap="medium")

        with res_col1:
            st.markdown("#### A. Policy Compliance Checker")
            violations = results.get("policy_violations", [])
            if violations:
                st.markdown(f"<div class='alert-danger-box'><strong>Detected {len(violations)} Violation(s):</strong></div>", unsafe_allow_html=True)
                for v in violations:
                    st.markdown(f"- ❌ **{v}**")
            else:
                st.markdown("<div class='alert-success-box'>✅ <strong>No policy violations detected.</strong> Response adheres to all company guidelines.</div>", unsafe_allow_html=True)

            st.markdown("#### B. False Promise Detection")
            fp_data = results.get("false_promises", {})
            fp_detected = fp_data.get("detected") or fp_data.get("false_promise_detected") == "Yes"

            if fp_detected:
                st.markdown("<div class='alert-warning-box'>⚠️ <strong>False Promise Alert:</strong> Unauthorized commitments detected in draft!</div>", unsafe_allow_html=True)
                statements = fp_data.get("suspicious_statements", [])
                if statements:
                    st.markdown("**Suspicious Commitment(s):**")
                    for s in statements:
                        st.markdown(f"> *\"{s}\"*")
                if fp_data.get("explanation"):
                    st.info(f"**Audit Note**: {fp_data.get('explanation')}")
            else:
                st.markdown("<div class='alert-success-box'>✅ <strong>No false promises.</strong> The response does not make unauthorized guarantees.</div>", unsafe_allow_html=True)

        with res_col2:
            st.markdown("#### C. Missing Information Detection")
            missing = results.get("missing_information", [])
            if missing:
                st.markdown(f"<div class='alert-warning-box'>⚠️ <strong>Missing Verification Details:</strong> {len(missing)} item(s) needed to resolve the case.</div>", unsafe_allow_html=True)
                for idx, item in enumerate(missing, 1):
                    item_name = item.get("item", f"Item #{idx}")
                    item_reason = item.get("reason", "Required by company guidelines.")
                    st.markdown(f"**{idx}. {item_name}**")
                    st.caption(f"Reason: {item_reason}")
            else:
                st.markdown("<div class='alert-success-box'>✅ <strong>All necessary customer details requested.</strong> No missing verification items.</div>", unsafe_allow_html=True)

    with tab_tone:
        st.markdown("#### D. Tone and Professionalism Analysis")
        scores = results.get("tone_scores", {})

        # Display 5 Scores in 5 Columns
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
                <div class="metric-box">
                    <div class="metric-value">{val} / 10</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
                # Visual Progress Bar
                st.progress(max(0.0, min(1.0, val / 10.0)))

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### Overall Tone Assessment")
        st.info(results.get("tone_assessment", "No tone assessment available."))

        st.markdown("##### Recommendations for Improvement")
        suggestions = results.get("improvement_suggestions", [])
        if suggestions:
            for s in suggestions:
                st.markdown(f"- 💡 {s}")
        else:
            st.markdown("- No additional improvements required.")

    with tab_improved:
        st.markdown("#### E. Final Improved Customer Support Response")
        st.caption("Policy-compliant, empathetic, and free of unauthorized promises.")

        imp_col1, imp_col2 = st.columns([1, 1], gap="medium")

        with imp_col1:
            st.markdown("**Original AI Draft (Part 1)**")
            st.text_area(
                "Original Draft",
                value=response_input,
                height=260,
                disabled=True,
                label_visibility="collapsed"
            )

        with imp_col2:
            st.markdown("**ChillGPT Improved Response (Part 2 Validated)**")
            improved_text = results.get("improved_response", "No improved response generated.")
            st.text_area(
                "Improved Response",
                value=improved_text,
                height=260,
                key="improved_response_box",
                label_visibility="collapsed"
            )

        st.markdown("##### Ready to Copy & Dispatch")
        st.code(improved_text, language="markdown")

    with tab_json:
        st.markdown("#### Structured JSON Payload (For Part 1 Integration)")
        st.caption("This structured output is directly returned by `review_response(...)` to the caller.")
        st.json(results)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 12px;'>"
    "ChillGPT Mini-Project &bull; Part 2: Response Review & Policy Validation Module &bull; Member 2 (Vedant)"
    "</div>",
    unsafe_allow_html=True
)
