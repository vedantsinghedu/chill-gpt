# ChillGPT – Customer Support Response Assistant ❄️

**Course Project:** Prompt Engineering  
**Role Scope:** **Part 1: Complaint Analysis and Response Generation**  
**Technology Stack:** Python 3.10+ | Streamlit | Prompt Engineering (Few-Shot, Grounding Guardrails, Tone Steering)

---

## 📌 Project Overview
**ChillGPT** is an intelligent AI-powered customer support assistant engineered to de-escalate customer complaints with empathy and professionalism while strictly adhering to company policies.

### Division of Work:
- **Part 1 (This Module):** **Complaint Analysis & Response Generation**
  - Ingests customer complaints and company policies.
  - Analyzes the complaint to extract:
    1. **Main Issue**
    2. **Customer Sentiment** (with intensity and rationale)
    3. **Category of Complaint**
    4. **Important Details** (Order ID, product name, dates, demands, customer name)
  - Enforces **Policy Grounding Guardrails** (never promises refunds, replacements, or compensations not backed by policy).
  - Drafts a tailored response in the chosen tone (**Professional**, **Friendly**, or **Empathetic**).
  - Prepares the standardized handoff package for Part 2.
- **Part 2 (Teammate's Module):** **Review & Validation Module** (to be integrated separately).

---

## 🚀 Key Features of Part 1

1. **Intelligent Complaint Analysis**:
   - Structured JSON prompt extraction.
   - Categorizes complaints into *Product Defect*, *Delivery & Shipping*, *Billing & Payments*, *Returns & Refunds*, etc.
   - Evaluates sentiment (*Angry*, *Frustrated*, *Anxious*, *Disappointed*, *Neutral*) with a 1–10 intensity score.

2. **Policy Grounding & Negative Guardrails**:
   - Closed-domain prompt constraint prevents AI hallucinations.
   - Detects customer demands that violate policy (e.g. requesting cash refunds for dropped devices or compensation for weather delays) and explicitly flags them as disallowed.
   - Instructs the generation prompt to decline out-of-policy requests politely while offering policy-approved alternatives.

3. **Multi-Tone Steering**:
   - **Professional**: Crisp, courteous, structured, formal, and reassuring.
   - **Friendly**: Warm, conversational, human, and partner-oriented.
   - **Empathetic**: Deep emotional validation, sincere remorse, and compassionate phrasing.

4. **Modular Architecture & Teammate Handoff**:
   - The generated response, analysis, and policy context are cleanly packaged in `st.session_state["handoff_data"]` and wrapped by `DraftResponseHandoff` in `modules/reviewer_interface.py`.
   - Your teammate can inspect the payload or import the hook without touching the core UI.

5. **Demo-Ready Modes**:
   - **Offline Simulator Mode**: Deterministic heuristic engine that follows prompt engineering rules without requiring an external API key or token credits (ideal for offline classroom demos & grading).
   - **Live LLM Mode**: Supports Google Gemini REST API and OpenAI-compatible APIs (Groq, Ollama, OpenAI) via simple sidebar configuration.

---

## 📂 Project Architecture

```
chillgpt/
├── app.py                     # Streamlit frontend & pipeline orchestrator
├── config.py                  # UI themes, CSS styling, and data loaders
├── requirements.txt           # Dependencies
├── README.md                  # Project & integration documentation
├── data/
│   ├── sample_policies.json   # Realistic company policies (Electronics, E-Commerce, SaaS)
│   └── sample_complaints.json # Realistic test scenarios (Dropped laptop, defective item, etc.)
└── modules/
    ├── __init__.py            # Package exports
    ├── prompts.py             # Prompt engineering templates, system prompts, guardrails
    ├── llm_client.py          # Unified client (Gemini REST, OpenAI REST, Offline Simulator)
    ├── analyzer.py            # Part 1A: Complaint Analyzer (JSON extraction)
    ├── generator.py           # Part 1B: Response Generator (Tone-steered drafting)
    └── reviewer_interface.py  # Teammate Integration Hook (Data Contract for Part 2)
```

---

## 🛠️ How to Run Locally

### 1. Clone / Open the Project Folder
Open your terminal or command prompt in the `chillgpt` directory:
```bash
cd d:\chillgpt
```

### 2. Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit App
```bash
streamlit run app.py
```
Streamlit will automatically open in your default browser at `http://localhost:8501`.

---

## 🎯 How to Demo the Project in Class

1. **Load a Pre-configured Scenario:**
   In the sidebar under **"Quick Test Scenarios"**, select:
   - **Scenario 1:** *Broken Screen - Demanding Instant Full Refund (Outside Policy)*
   - Click **"Load Selected Scenario"**.
2. **Observe the Grounding Guardrail:**
   - The customer broke their screen by dropping it and is demanding a full cash refund and $100 compensation.
   - The policy excludes drop damage from warranty and has a 14-day unopened return limit.
3. **Select Tone:**
   - Pick **Empathetic**, **Professional**, or **Friendly**.
4. **Click "🚀 Analyze Complaint & Generate Response":**
   - Review **Part 1 Analysis** showing sentiment (*Angry 9/10*), Category (*Product Defect*), and Policy Compliance (*⚠️ Out-of-Policy Demands*).
   - Review **Generated Customer Support Response**: Notice how it validates the customer's frustration, politely declines the refund/compensation citing policy, and offers the policy-approved 20% discount on certified repair!
5. **Inspect Prompt Engineering Details:**
   - Open the **"Prompt Engineering Inspector"** accordion to show the professor the exact System Prompt, Negative Constraints, and Structured Prompt Templates!
6. **Show Teammate Handoff:**
   - Expand **"Teammate Handoff: Ready for Part 2"** to show the standardized JSON payload exported to `st.session_state["handoff_data"]`.

---

## 🤝 Teammate Integration Guide (For Part 2: Review & Validation)

Your teammate can easily attach their Part 2 module using either of the following approaches:

### Option A: Read from Session State in Streamlit
```python
import streamlit as st

# Retrieve the handoff data generated by Part 1
handoff = st.session_state.get("handoff_data")

if handoff:
    complaint = handoff["complaint_text"]
    policy = handoff["company_policy"]
    analysis = handoff["analysis"]
    draft = handoff["draft_response"]
    tone = handoff["tone"]
    
    # Run your Part 2 validation rules here!
```

### Option B: Inherit from `ReviewerModuleInterface`
In `modules/reviewer_interface.py`:
```python
from modules.reviewer_interface import ReviewerModuleInterface, DraftResponseHandoff

class MyValidationModule(ReviewerModuleInterface):
    def validate_draft(self, handoff: DraftResponseHandoff):
        # 1. Check policy compliance score
        # 2. Check tone consistency
        # 3. Output review verdict
        return {"status": "PASSED", "score": 95}
```
