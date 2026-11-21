"""
Response Reviewer Module for ChillGPT (Part 2).
Coordinates AI-powered evaluation via Gemini API with strict JSON schema parsing,
and provides a reliable deterministic local validation fallback when API key is unavailable.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv

# Import local deterministic validator engines
from modules.policy_validator import validate_policy
from modules.false_promise_detector import detect_false_promises
from modules.information_checker import check_missing_information
from modules.tone_analyzer import analyze_tone

# Load environment variables from .env
load_dotenv()


def _load_prompt_template() -> str:
    """Loads the production prompt from prompts/final/review_prompt.txt."""
    candidates = [
        Path(__file__).parent.parent / "prompts" / "final" / "review_prompt.txt",
        Path.cwd() / "prompts" / "final" / "review_prompt.txt",
        Path.cwd() / "ChillGPT-Reviewer" / "prompts" / "final" / "review_prompt.txt",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")

    return (
        "Evaluate the following support response against policy and complaint.\n"
        "Customer Complaint: {customer_complaint}\n"
        "Company Policy: {company_policy}\n"
        "Generated Response: {generated_response}\n"
        "Return valid JSON only matching schema."
    )


def _clean_json_output(raw_text: str) -> str:
    """Strips markdown code fences and extraneous text from LLM response."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1]
    return text


def _generate_deterministic_improved_response(
    customer_complaint: str,
    company_policy: str,
    generated_response: str,
    missing_info: list,
    compliance_status: str
) -> str:
    """Synthesizes a policy-compliant, empathetic, and actionable improved response."""
    lines = [
        "Dear Valued Customer,",
        "",
        "Thank you for contacting customer support. We sincerely apologize for the frustration "
        "and inconvenience you have experienced with your purchase. We understand how disappointing "
        "this situation is and are committed to helping you resolve it promptly.",
        ""
    ]

    policy_lower = company_policy.lower() if company_policy else ""

    if "no refund" in policy_lower or "final sale" in policy_lower or "non-refundable" in policy_lower:
        lines.append(
            "Please note that under our company policy, sales are considered final and standard refunds "
            "cannot be processed. However, our team is eager to review your case for any applicable manufacturer "
            "warranty, repair assistance, or troubleshooting support."
        )
    elif "inspection" in policy_lower or "unboxing" in policy_lower or "3-5" in policy_lower or "5-7" in policy_lower:
        lines.append(
            "Under our store policy, return and refund requests undergo an inspection upon receipt at our "
            "fulfillment center. Once your return is received and verified against policy guidelines, "
            "eligible refunds are processed directly to your original payment method within standard bank processing timelines."
        )
    else:
        lines.append(
            "We want to ensure your issue is thoroughly investigated and resolved in accordance with our store policies."
        )

    lines.append("")

    if missing_info:
        lines.append("To allow our team to proceed with your investigation, could you please provide:")
        for item in missing_info:
            name = item.get("item", "Required details")
            lines.append(f"• {name}")
        lines.append("")
        lines.append("Once we receive this information, we will immediately initiate the next steps.")
    else:
        lines.append(
            "Our support team is actively reviewing your case details and will follow up with the next update shortly."
        )

    lines.append("")
    lines.append("Thank you for your patience and understanding.")
    lines.append("")
    lines.append("Warm regards,")
    lines.append("ChillGPT Customer Support Team")

    return "\n".join(lines)


def _run_deterministic_evaluation(
    customer_complaint: str,
    company_policy: str,
    generated_response: str,
    reason: str = "Deterministic Local Validation Mode (Gemini API key not configured)"
) -> Dict[str, Any]:
    """Runs deterministic local checks across all 4 sub-modules."""
    policy_res = validate_policy(customer_complaint, company_policy, generated_response)
    false_promise_res = detect_false_promises(company_policy, generated_response)
    info_res = check_missing_information(customer_complaint, company_policy, generated_response)
    tone_res = analyze_tone(generated_response)

    # Combine violations and unsupported claims
    all_violations = list(policy_res.get("violations", []))
    if policy_res.get("unsupported_claims"):
        all_violations.extend(policy_res.get("unsupported_claims", []))

    status = policy_res.get("compliance_status", "Compliant")
    # If false promises are detected, status cannot remain Compliant
    if false_promise_res.get("detected"):
        if status == "Compliant":
            status = "Non-Compliant"
        # Also ensure false promise explanations are visible in violations if empty
        if not all_violations and false_promise_res.get("suspicious_statements"):
            all_violations.append(f"Unauthorized promise detected: {false_promise_res.get('explanation')}")

    improved_resp = _generate_deterministic_improved_response(
        customer_complaint=customer_complaint,
        company_policy=company_policy,
        generated_response=generated_response,
        missing_info=info_res.get("missing_information", []),
        compliance_status=status
    )

    return {
        "compliance_status": status,
        "policy_violations": all_violations,
        "false_promises": {
            "detected": false_promise_res.get("detected", False),
            "false_promise_detected": false_promise_res.get("false_promise_detected", "No"),
            "suspicious_statements": false_promise_res.get("suspicious_statements", []),
            "explanation": false_promise_res.get("explanation", "")
        },
        "missing_information": info_res.get("missing_information", []),
        "tone_scores": tone_res.get("scores", {
            "professionalism": 7,
            "empathy": 5,
            "politeness": 6,
            "clarity": 7,
            "customer_friendliness": 6
        }),
        "tone_assessment": tone_res.get("tone_assessment", ""),
        "improvement_suggestions": tone_res.get("suggestions", []),
        "improved_response": improved_resp,
        "analysis_mode": "deterministic_fallback",
        "engine_details": reason
    }


def review_response(
    customer_complaint: str,
    company_policy: str,
    generated_response: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main reusable review function required for Part 1 integration.

    Evaluates the generated customer support response against the company policy
    and customer complaint using Gemini AI (if configured) or deterministic local logic.

    Args:
        customer_complaint: Grievance text submitted by the customer.
        company_policy: Operational store guidelines and terms.
        generated_response: Support response drafted by Part 1 or support agent.
        api_key: Optional Gemini API key. If not provided, reads from GEMINI_API_KEY env.

    Returns:
        dict containing:
            - compliance_status (str): "Compliant" | "Partially Compliant" | "Non-Compliant"
            - policy_violations (List[str])
            - false_promises (dict): {detected: bool, suspicious_statements: list, explanation: str}
            - missing_information (List[dict]): [{item: str, reason: str}]
            - tone_scores (dict): {professionalism, empathy, politeness, clarity, customer_friendliness} (1-10)
            - tone_assessment (str)
            - improvement_suggestions (List[str])
            - improved_response (str)
            - analysis_mode (str): "ai_gemini" | "deterministic_fallback"
            - engine_details (str)
    """
    complaint_clean = (customer_complaint or "").strip()
    policy_clean = (company_policy or "").strip()
    response_clean = (generated_response or "").strip()

    key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()

    if not key:
        return _run_deterministic_evaluation(
            complaint_clean,
            policy_clean,
            response_clean,
            reason="Deterministic Local Validation Mode: No GEMINI_API_KEY configured."
        )

    try:
        from google import genai
        from google.genai import types

        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()
        client = genai.Client(api_key=key)

        prompt_template = _load_prompt_template()
        prompt = prompt_template.format(
            customer_complaint=complaint_clean if complaint_clean else "[No complaint provided]",
            company_policy=policy_clean if policy_clean else "[No policy provided]",
            generated_response=response_clean if response_clean else "[Empty response]"
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            )
        )

        raw_output = response.text or ""
        cleaned_json = _clean_json_output(raw_output)
        parsed = json.loads(cleaned_json)

        required_keys = [
            "compliance_status", "policy_violations", "false_promises",
            "missing_information", "tone_scores", "tone_assessment",
            "improvement_suggestions", "improved_response"
        ]
        for rk in required_keys:
            if rk not in parsed:
                parsed[rk] = [] if "s" in rk else ""

        if isinstance(parsed["false_promises"], dict):
            if "false_promise_detected" not in parsed["false_promises"]:
                parsed["false_promises"]["false_promise_detected"] = (
                    "Yes" if parsed["false_promises"].get("detected") else "No"
                )

        parsed["analysis_mode"] = "ai_gemini"
        parsed["engine_details"] = f"Evaluated using Google Gemini ({model_name})"
        return parsed

    except Exception as exc:
        fallback_result = _run_deterministic_evaluation(
            complaint_clean,
            policy_clean,
            response_clean,
            reason=f"Deterministic Local Validation Mode (Gemini API unavailable: {type(exc).__name__} - {str(exc)})"
        )
        return fallback_result
