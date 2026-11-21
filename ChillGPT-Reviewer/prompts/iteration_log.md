# ChillGPT Prompt Engineering & Iteration Log
**Module**: Part 2 - Response Review and Policy Validation  
**Author**: Member 2 (Vedant)  
**Target LLM**: Google Gemini 2.5 Flash / Gemini Pro API  

---

## Overview

The prompt for the Response Reviewer module is designed to evaluate an AI-generated customer support response against both the company's operating policy and the customer's original complaint. The evaluation must be deterministic in format, comprehensive in analysis, and capable of generating a corrected, policy-compliant response.

Below is the documented iteration cycle tracking how the prompt evolved from initial prototype (V1) to the production prompt (FINAL).

---

## Prompt Versions

### Version 1 (V1): Initial Baseline
* **File**: `prompts/v1/review_prompt.txt`
* **Objective**: Basic instruction to check if the generated response follows company policy and identify obvious errors.
* **Key Content**:
  - Unstructured instructions.
  - Asks generic questions: "Check if the response follows the company policy", "Tell me if there are any mistakes", "Suggest an improved response".
* **Rationale for Changes**:
  - V1 was an initial zero-shot baseline to verify raw LLM capability.
* **Observed Limitations**:
  - LLM produced conversational, free-form text with inconsistent structure.
  - Fails to parse programmatically in Python (`json.loads` fails).
  - Missed subtle false promises (e.g. promising immediate refunds before return inspection).
  - Did not check if order numbers or damage photos were missing.
  - No numerical scoring of tone or professionalism.
* **Execution Observations**:
  - Free-form text was unparseable by backend integrations.
  - Inconsistent classification terms (e.g., "Violates policy slightly", "Not bad", "Unacceptable").

---

### Version 2 (V2): Targeted Multi-Task Audit
* **File**: `prompts/v2/review_prompt.txt`
* **What Changed**:
  - Added specific sub-tasks for:
    1. Policy Compliance (Compliant / Partially Compliant / Non-Compliant).
    2. False Promise Detection (unauthorized refunds, delivery guarantees, compensation).
    3. Missing Information Detection (Order ID, photo evidence, tracking).
    4. Improved Response generation.
* **Why the Change Was Made**:
  - Ground the LLM into specific audit dimensions rather than generic feedback.
  - Explicitly force detection of unauthorized commitments.
* **Observed Limitations**:
  - Output was still formatted in Markdown bullet points rather than machine-readable JSON.
  - Tone was discussed qualitatively without standardized metrics.
  - Over-flagged missing information (flagged "order ID" even when the customer already provided it in the complaint).
* **Execution Observations**:
  - Improved audit accuracy significantly over V1, but could not be integrated into an automated pipeline due to markdown formatting.

---

### Version 3 (V3): Structured JSON Schema & Quantitative Tone Scoring
* **File**: `prompts/v3/review_prompt.txt`
* **What Changed**:
  - Defined a strict JSON output schema.
  - Introduced 5 quantitative tone metrics on a 1-10 scale:
    - `professionalism`
    - `empathy`
    - `politeness`
    - `clarity`
    - `customer_friendliness`
  - Added fields for `tone_assessment` and `improvement_suggestions`.
  - Added instructions to return raw JSON only.
* **Why the Change Was Made**:
  - Ensure deterministic output structure for seamless Python dictionary parsing by Part 1 and UI consumers.
  - Quantify tone metrics for Streamlit dashboard visualization.
* **Observed Limitations**:
  - LLM sometimes wrapped output in markdown code fences (\`\`\`json ... \`\`\`), requiring string stripping.
  - Occasionally invented compensation policies (e.g. suggesting a $10 coupon) in the improved response when the policy did not authorize one.
  - On edge cases (e.g., customer complaints that already contained order numbers), occasionally still flagged order numbers as missing.
* **Execution Observations**:
  - JSON parsing succeeded 90% of the time, but edge cases required strict boundary constraints and explicit negative prompt rules.

---

### Final Production Version (FINAL): Strict Enterprise Compliance Prompt
* **File**: `prompts/final/review_prompt.txt`
* **What Changed**:
  - **Explicit Negative Constraints**:
    - "NEVER invent imaginary refund, replacement, or compensation policies."
    - "CRITICAL: Do NOT flag information that the customer has already provided in the complaint. Only flag what is actually missing and necessary."
    - "Preserve the actual meaning of the customer's complaint."
  - **Strict JSON Schema & Directives**:
    - "Respond strictly with a valid JSON object matching this exact schema."
    - "Do not include any prose outside the JSON object. Do not wrap the output in markdown codeblocks."
  - **Granular Criteria for Compliance**:
    - Explicit definitions for "Compliant", "Partially Compliant", and "Non-Compliant".
    - Categorized false promise triggers (instant refund vs unboxing video requirement, shipping guarantees, unauthorized replacement).
  - **Tone Definitions**:
    - Explicit rubrics for 1-10 scoring on all 5 parameters.
* **Why the Change Was Made**:
  - Eliminate hallucinations and unsupported commitments in the improved response.
  - Guarantee 100% schema compliance for direct deserialization in `review_response(...)`.
  - Prevent false positive missing information alerts when details are already present.
* **Execution Observations**:
  - High fidelity across edge cases (empty inputs, hostile tone, unauthorized refunds).
  - Clean JSON format directly parseable by Python.
  - Reliable deterministic fallback synchronization when running in offline/no-key mode.

---

## Summary Comparison Table

| Metric / Feature | V1 | V2 | V3 | FINAL |
| :--- | :--- | :--- | :--- | :--- |
| **Output Format** | Unstructured text | Markdown headers/bullets | JSON (loose) | Strict JSON Schema |
| **Machine Parseable** | No | No | ~90% | 100% (with sanitizer) |
| **Policy Violation Check** | Basic | Detailed | Detailed | Detailed with categorization |
| **False Promise Detection** | None | Explicit | Explicit | Explicit with suspicious quotes |
| **Missing Info Logic** | None | Over-flagged | Filtered | Context-aware (no false positives) |
| **Tone Scoring (1-10)** | None | Qualitative only | 5 Metrics | 5 Metrics with clear rubrics |
| **Improved Response Quality**| Generic | Policy-aligned | Good | Policy-strict, empathetic, no hallucinations |
