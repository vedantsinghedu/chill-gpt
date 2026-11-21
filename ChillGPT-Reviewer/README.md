# ChillGPT — Customer Support Response Assistant
## Part 2: Response Review and Policy Validation Module
**Project**: College Mini-Project  
**Author**: Member 2 (Vedant)  
**Collaborator**: Member 1 (Responsible for Part 1: Complaint Analysis & Initial Response Generation)  

---

## 1. Project Overview & Architecture

**ChillGPT** is an AI-powered customer support response assistant built for small e-commerce businesses. It assists merchants in generating professional, empathetic, and policy-compliant responses to customer grievances.

The system is developed collaboratively by two team members:
- **Part 1 (Member 1)**: Ingests the customer complaint and company policy, analyzing sentiment and drafting an initial AI response.
- **Part 2 (Member 2 - Vedant)**: Acts as the quality gate and policy compliance reviewer. It inspects the draft response for policy violations, false promises, missing verification data, and tone quality, before generating an improved, final customer-facing response.

```
┌─────────────────────────────────┐
│     Customer Complaint          │
│     & Company Policy            │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│    Part 1: Draft Generator      │  (Developed by Member 1)
│    (Initial Response Draft)     │
└───────────────┬─────────────────┘
                │  Initial Draft Response
                ▼
┌───────────────────────────────────────────────────────────┐
│      Part 2: Response Review & Policy Validation          │  (Developed by Member 2 - Vedant)
│                                                           │
│  ├─ Policy Compliance Checker (validate_policy)           │
│  ├─ False Promise Detection (detect_false_promises)       │
│  ├─ Missing Information Detection (check_missing_info)    │
│  ├─ Tone & Professionalism Scoring (analyze_tone)         │
│  └─ Production Prompt Engine (Gemini API / Local Fallback)│
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│   Final Verified Response       │
│   + Audit Quality Dashboard     │
└─────────────────────────────────┘
```

---

## 2. Implemented Functionalities (Part 2)

### A. Policy Compliance Checker (`modules/policy_validator.py`)
- Analyzes the generated response against specific policy clauses (return windows, refund restrictions, inspection rules, final sale conditions).
- Categorizes status into: **Compliant**, **Partially Compliant**, or **Non-Compliant**.
- Detects direct violations and unsupported claims, providing detailed explanations.

### B. False Promise Detection (`modules/false_promise_detector.py`)
- Scans for unauthorized commitments not permitted under company guidelines:
  - Immediate/unconditional refund promises before return or inspection.
  - Delivery guarantees (e.g., next-day arrival) without carrier verification.
  - Unauthorized monetary compensation, coupons, vouchers, or store credit.
  - Instant replacements without prerequisite defect verification.
- Extracts exact suspicious statements and provides audit reasoning.

### C. Missing Information Detection (`modules/information_checker.py`)
- Context-aware identification of critical missing information (Order ID, damage photos, unboxing videos, tracking numbers, transaction IDs).
- **Zero False Positives**: Does not flag information that the customer already provided in their complaint.
- Explains why each missing piece of information is required.

### D. Tone & Professionalism Analysis (`modules/tone_analyzer.py`)
- Scores the draft response across five key metrics on a strict **1 to 10 scale**:
  1. **Professionalism** (greetings, sign-offs, absence of slang or aggression)
  2. **Empathy** (acknowledgment of customer distress and sincere apology)
  3. **Politeness** (courtesy markers like "please", "kindly", "thank you")
  4. **Clarity** (readability, absence of rambling, structured next steps)
  5. **Customer-Friendliness** (supportive, solution-oriented phrasing)
- Produces a holistic qualitative tone assessment and actionable suggestions.

### E. Response Improvement (`modules/response_reviewer.py`)
- Synthesizes a polished, empathetic, and policy-compliant replacement response.
- Removes false promises and replaces them with authorized company procedures.
- Explicitly and politely requests any missing customer verification details.

---

## 3. Technology Stack

- **Python 3.10+** (Core programming language)
- **Streamlit** (Clean, SaaS-style blue and white testing interface)
- **Google Gemini API (`google-genai`)** (AI evaluation engine with structured JSON output)
- **Pytest** (Automated unit and integration test suite)
- **python-dotenv** (Secure API key and configuration management)

---

## 4. Installation & Setup Instructions

### Step 1: Clone or Navigate to the Workspace
```bash
cd /Users/vedant/Documents/CHILL-GPT/ChillGPT-Reviewer
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. Gemini API Configuration

1. Copy `.env.example` to create a local `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and paste your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. **Deterministic Local Mode (No Key Required)**:
   If `GEMINI_API_KEY` is omitted or empty, ChillGPT operates in **Deterministic Local Validation Mode**. It runs full rule-based heuristic checks and clearly marks `analysis_mode: "deterministic_fallback"`. It never pretends an AI call was made.

---

## 6. How to Run the Application Interface

Launch the standalone Streamlit testing interface:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### Interface Features:
1. **Scenario Selector**: Load 5 pre-configured e-commerce test cases in 1 click.
2. **Side-by-Side Review**: Compare original AI response against company policy.
3. **Audit Dashboard**: View compliance badge, false promise warnings, and missing info alerts.
4. **Tone Metric Visualizers**: 5 progress bars showing scores from 1 to 10.
5. **One-Click Copy**: Copy the improved response ready for dispatch.
6. **JSON Debugger**: Inspect the structured payload for Part 1 integration.

---

## 7. How to Run Tests

Execute the comprehensive test suite with Pytest:

```bash
pytest tests/ -v
```

---

## 8. Test Execution Results (18/18 Passed)

All 10 required test scenarios, 5 edge cases, and 3 API contract tests have been executed and verified:

| Test ID | Scenario / Input | Expected Output | Actual Output | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TEST-01** | Order #1029 broken zipper; response asks for photo and explains policy | `Compliant`, 0 violations, False promises: No | Status: `Compliant`, Violations: `[]`, False promises: `No` | **PASS** |
| **TEST-02** | Final sale footwear; response promises immediate refund to card | `Non-Compliant`, refund violation, False promises: Yes | Status: `Non-Compliant`, Detected refund violation, False promise: `Yes` | **PASS** |
| **TEST-03** | Replacement requires return; response promises immediate dispatch | `Non-Compliant`, replacement violation, False promises: Yes | Status: `Non-Compliant`, Flagged instant replacement dispatch | **PASS** |
| **TEST-04** | Delayed package inquiry; response fails to ask for Order ID | Flag `Order ID / Invoice Number` in `missing_information` | Flagged: `Order ID / Invoice Number` with database lookup reasoning | **PASS** |
| **TEST-05** | Hostile/slang response ("Bro chill out lol read the website") | Professionalism <= 5, Politeness <= 5, Slang penalized | Professionalism: `2/10`, Politeness: `2/10`, Slang suggestions flagged | **PASS** |
| **TEST-06** | Standard shipping policy; response guarantees delivery tomorrow morning | `Partially Compliant` / `Non-Compliant`, Delivery false promise | Status: `Partially Compliant`, Flagged tomorrow delivery guarantee | **PASS** |
| **TEST-07** | Multiple violations: instant refund + $50 gift card + instant replacement | `Non-Compliant`, multiple violations detected | Status: `Non-Compliant`, Detected 3 distinct violations | **PASS** |
| **TEST-08** | Polite deflection ("Have a blessed day!") with zero resolution | `Partially Compliant`, flags missing order details & zero resolution | Status: `Partially Compliant`, Flagged missing info & zero substance | **PASS** |
| **TEST-09** | Empty generated response (`"   "`) | `Non-Compliant`, flags empty response, Professionalism: 1 | Status: `Non-Compliant`, Professionalism: `1/10` | **PASS** |
| **TEST-10** | Incomplete/unclear company policy (`"Returns."`) | `Partially Compliant`, flags policy ambiguity | Status: `Partially Compliant`, Flagged brief/unspecified policy | **PASS** |
| **EC-01** | All empty/whitespace inputs (complaint, policy, response) | Handled safely without crash, `Non-Compliant` | Handled gracefully, returns structured fallback dictionary | **PASS** |
| **EC-02** | Complaint already has Order #99281 and attached photo | Do NOT falsely flag Order ID or photo as missing | Neither Order ID nor photo flagged as missing | **PASS** |
| **EC-03** | Massive verbose input (1500-word complaint and long policy) | Stress test handled without memory or token crash | Successfully audited, `Compliant` | **PASS** |
| **EC-04** | Slang and emojis in response (`💀💀, fr fr, slide into warehouse`) | Tone analyzer penalizes heavy informal diction | Professionalism: `4/10`, Slang warning generated | **PASS** |
| **EC-05** | Conflicting policy clauses (7-day returns vs strictly non-refundable) | Identifies unauthorized cash refund commitment | Status: `Non-Compliant`, False promise: `Yes` | **PASS** |
| **API-01** | Public API schema integrity check | Returns all 8 required dictionary keys | All 8 required keys present with valid types | **PASS** |
| **API-02** | Tone scores numerical boundaries | All 5 metrics are integers between 1 and 10 | All 5 metrics verified in range [1, 10] | **PASS** |
| **API-03** | Deterministic fallback mode tag | Explicitly sets `analysis_mode: deterministic_fallback` | Flag verified: `deterministic_fallback` | **PASS** |

---

## 9. Integration Guide for Member 1

Member 1 can directly integrate Part 2 using the following clean Python interface:

```python
from modules.response_reviewer import review_response

# Pass complaint, policy, and your generated draft from Part 1
audit_report = review_response(
    customer_complaint=complaint_text,
    company_policy=policy_text,
    generated_response=part1_draft_response
)

# Extract key validation results
compliance = audit_report["compliance_status"]      # "Compliant" | "Partially Compliant" | "Non-Compliant"
violations = audit_report["policy_violations"]      # List of strings
false_promises = audit_report["false_promises"]     # {"detected": bool, "suspicious_statements": list, ...}
missing_info = audit_report["missing_information"]  # [{"item": "...", "reason": "..."}]
tone_scores = audit_report["tone_scores"]           # {"professionalism": 8, "empathy": 9, ...}
final_response = audit_report["improved_response"]  # Ready-to-send safe response
```

For full details, see [docs/integration_guide.md](docs/integration_guide.md).

---

## 10. Prompt Engineering Iteration

Prompt revisions are tracked under the `prompts/` directory:
- `prompts/v1/review_prompt.txt`: Initial zero-shot baseline.
- `prompts/v2/review_prompt.txt`: Multi-task audit covering policy, false promises, and missing information.
- `prompts/v3/review_prompt.txt`: Introduced structured JSON schema and 5-dimension tone scoring.
- `prompts/final/review_prompt.txt`: Production prompt with negative constraints, few-shot rules, and strict schema.
- `prompts/iteration_log.md`: Detailed changelog and prompt engineering rationale.
