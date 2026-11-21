# ChillGPT — Customer Support Response Assistant ❄️

**Course Project:** Prompt Engineering / College Mini-Project  
**Repository:** [https://github.com/vedantsinghedu/chill-gpt](https://github.com/vedantsinghedu/chill-gpt)  
**Technology Stack:** Python 3.10+ | Streamlit | Google Gemini API | Heuristic Validation Logic | Pytest

---

## 📌 Project Overview

**ChillGPT** is an intelligent AI-powered customer support assistant engineered to help e-commerce businesses de-escalate customer complaints with empathy and professionalism while strictly adhering to company policies.

The project is developed collaboratively in two specialized parts:
- **Part 1 (Member 1 - Kumari Ishani)**: **Complaint Analysis & Initial Response Generation**
  - Ingests complaints and policies.
  - Analyzes sentiment (1–10 intensity), categories, and important details.
  - Generates initial responses steered by tone (*Empathetic*, *Professional*, *Friendly*).
  - Prepares the standardized handoff package via `DraftResponseHandoff`.
- **Part 2 (Member 2 - Vedant)**: **Response Review & Policy Validation Module**
  - Audits the generated response against company policy for compliance.
  - Detects false promises (unauthorized instant refunds, delivery guarantees, unapproved vouchers).
  - Flags missing critical details (Order ID, photo/video proof) without false positives.
  - Scores response tone across 5 dimensions (1–10).
  - Generates a polished, policy-compliant, and empathetic improved response.

---

## 🏛️ System Architecture & Workflow

```
┌─────────────────────────────────┐
│     Customer Complaint          │
│     & Company Policy            │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│   Part 1: Draft Generator       │ (Developed by Member 1)
│   (Complaint Analysis & Draft)  │
└───────────────┬─────────────────┘
                │ Standardized DraftResponseHandoff
                ▼
┌─────────────────────────────────────────────────────────────┐
│  Part 2: review_response(...) [Quality Gate & Reviewer]     │ (Developed by Member 2 - Vedant)
│                                                             │
│  ├─ Policy Compliance Checker (validate_policy)             │
│  ├─ False Promise Detection (detect_false_promises)         │
│  ├─ Missing Information Detection (check_missing_info)      │
│  ├─ Tone & Professionalism Scoring (analyze_tone)           │
│  └─ Gemini AI + Deterministic Local Fallback Engine         │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│   Final Verified Response       │
│   + Full Audit Dashboard        │
└─────────────────────────────────┘
```

---

## 📂 Repository Structure

```
chill-gpt/
├── app.py                         # Part 1: Main Streamlit frontend & pipeline orchestrator
├── config.py                      # Part 1: UI themes, styling, and data loaders
├── requirements.txt               # Project dependencies
├── test_module.py                 # Part 1: Unit tests
├── test_5_cases.py                # Part 1: 5-scenario evaluation tests
├── data/                          # Sample complaints and policies
│   ├── sample_complaints.json
│   └── sample_policies.json
│
├── modules/                       # Part 1 Modules
│   ├── analyzer.py                # Complaint sentiment & category extraction
│   ├── generator.py               # Tone-steered draft response generator
│   ├── llm_client.py              # Gemini / OpenAI REST & Offline Simulator
│   ├── prompts.py                 # Grounded prompts & few-shot templates
│   └── reviewer_interface.py      # Handoff interface between Part 1 and Part 2
│
└── ChillGPT-Reviewer/             # Part 2: Review & Policy Validation Module (Member 2)
    ├── app.py                     # Part 2: Standalone SaaS testing dashboard
    ├── requirements.txt           # Part 2 dependencies
    ├── .env.example               # Gemini API environment template
    ├── README.md                  # Comprehensive Part 2 documentation & test logs
    ├── docs/
    │   └── integration_guide.md   # Integration specs for connecting Part 1 & Part 2
    ├── modules/
    │   ├── response_reviewer.py   # Core coordinator implementing review_response()
    │   ├── policy_validator.py    # Policy compliance checking
    │   ├── false_promise_detector.py # Unauthorized commitment detection
    │   ├── information_checker.py # Contextual missing info detector
    │   └── tone_analyzer.py       # 5-parameter tone scoring (1–10)
    ├── prompts/
    │   ├── v1/, v2/, v3/, final/  # Versioned prompt engineering progression
    │   └── iteration_log.md       # Documented prompt evolution & rationale
    └── tests/
        ├── test_policy.py         # 10 comprehensive policy test scenarios
        ├── test_reviewer.py       # Public API contract & schema tests
        └── test_edge_cases.py     # Boundary & edge case tests
```

---

## 🚀 Quick Start Guide

### 1. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r ChillGPT-Reviewer/requirements.txt
```

### 2. Run Part 2 Test Suite (18/18 Passing)
```bash
pytest ChillGPT-Reviewer/tests/ -v
```

### 3. Launch Part 2 Reviewer Interface
```bash
cd ChillGPT-Reviewer
streamlit run app.py
```
Open `http://localhost:8501` to test the policy validator, false promise detector, tone metrics, and improved response generator.

### 4. Launch Part 1 Generation Interface
```bash
streamlit run app.py
```

---

## 🤝 How Both Modules Integrate

Member 2's validation module directly consumes the `DraftResponseHandoff` payload from Member 1:

```python
from ChillGPT_Reviewer.modules.response_reviewer import review_response

# Call Part 2 review function using Part 1 handoff data
audit_report = review_response(
    customer_complaint=handoff.complaint_text,
    company_policy=handoff.company_policy,
    generated_response=handoff.draft_response
)

print(audit_report["compliance_status"])     # "Compliant" | "Partially Compliant" | "Non-Compliant"
print(audit_report["policy_violations"])     # List of specific policy violations
print(audit_report["false_promises"])        # Detected unauthorized commitments
print(audit_report["tone_scores"])           # {"professionalism": 8, "empathy": 9, ...}
print(audit_report["improved_response"])     # Safe, final response for the customer
```

For detailed integration guides, see [`ChillGPT-Reviewer/docs/integration_guide.md`](ChillGPT-Reviewer/docs/integration_guide.md).
