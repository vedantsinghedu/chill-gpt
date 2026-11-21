"""
False Promise Detection Module for ChillGPT.
Identifies unauthorized commitments, instant refunds, delivery guarantees,
and unwarranted compensations in AI-generated customer support responses.
"""

import re
from typing import Dict, List, Any


def detect_false_promises(
    company_policy: str,
    generated_response: str
) -> Dict[str, Any]:
    """
    Scans the generated response for commitments not authorized by company policy.

    Args:
        company_policy: Authoritative company rules and guidelines.
        generated_response: Draft response to audit.

    Returns:
        dict: {
            "detected": bool,
            "false_promise_detected": "Yes" | "No",
            "suspicious_statements": List[str],
            "explanation": str
        }
    """
    clean_policy = (company_policy or "").strip().lower()
    clean_response = (generated_response or "").strip()

    if not clean_response:
        return {
            "detected": False,
            "false_promise_detected": "No",
            "suspicious_statements": [],
            "explanation": "No response text provided to evaluate for false promises."
        }

    suspicious_statements: List[str] = []
    reasons: List[str] = []

    # Split response into candidate sentences/clauses
    sentences = [s.strip() for s in re.split(r"[.\n!?;]+", clean_response) if s.strip()]

    # 1. Immediate / Unauthorized Refund Promises
    instant_refund_triggers = [
        r"refund.*(immediately|right\s+now|right\s+away|instantly|today)",
        r"(immediately|instantly|already|have)\s+processed.*refund",
        r"(issued|issue|process).*refund.*(directly\s+)?to\s+your\s+(credit\s+)?(card|account|bank)",
        r"guarantee.*(an\s+instant|immediate).*refund",
        r"money\s+back.*(today|immediately|right\s+now|right\s+away)",
        r"refund\s+you\s+(immediately|right\s+now|right\s+away|today)"
    ]
    requires_verification = any(term in clean_policy for term in [
        "inspect", "verification", "receipt", "unboxing", "return first", "after receiving", "3-5", "5-7"
    ]) or "no refund" in clean_policy or "non-refundable" in clean_policy or "final sale" in clean_policy

    for sentence in sentences:
        s_lower = sentence.lower()
        for trig in instant_refund_triggers:
            if re.search(trig, s_lower):
                if requires_verification or "instant" not in clean_policy:
                    if sentence not in suspicious_statements:
                        suspicious_statements.append(sentence)
                        reasons.append("Promises an immediate or unauthorized refund contrary to company policy.")
                    break

    # If policy strictly prohibits refunds, ANY affirmative refund promise is an unauthorized commitment
    is_strictly_non_refundable = any(term in clean_policy for term in [
        "no refund", "non-refundable", "non refundable", "final sale"
    ])
    if is_strictly_non_refundable:
        for sentence in sentences:
            s_lower = sentence.lower()
            if re.search(r"(issue|process|provide|give|send|approved?).*refund|refund.*(card|account)", s_lower):
                if sentence not in suspicious_statements:
                    suspicious_statements.append(sentence)
                    reasons.append("Promises a refund when company policy strictly specifies non-refundable or final sale.")

    # 2. Unsupported Delivery Guarantees
    delivery_guarantee_triggers = [
        r"guarantee.*(it will|your order will|delivery|arrival).*(tomorrow|within\s+\d+\s+hours)",
        r"will\s+definitely\s+(arrive|reach\s+you|deliver).*(tomorrow|within\s+\d+\s+hours)",
        r"guaranteed\s+(delivery|arrival)",
        r"(arrive|deliver).*(tomorrow\s+morning|tomorrow\s+without\s+fail)"
    ]
    has_overnight_guarantee_policy = "guaranteed next-day" in clean_policy or "overnight guaranteed" in clean_policy

    for sentence in sentences:
        s_lower = sentence.lower()
        for trig in delivery_guarantee_triggers:
            if re.search(trig, s_lower) and not has_overnight_guarantee_policy:
                if sentence not in suspicious_statements:
                    suspicious_statements.append(sentence)
                    reasons.append("Guarantees delivery timing without carrier confirmation or policy backing.")
                break

    # 3. Unauthorized Monetary Compensation / Vouchers
    compensation_triggers = [
        r"(gift\s*card|voucher|store\s*credit|coupon|compensation)\s+of\s+\$\d+",
        r"(\$\d+|\d+%\s*(discount|off)).*(gift\s*card|voucher|credit|coupon)",
        r"give\s+you\s+(a\s+)?(\$\d+|\d+%).*(gift\s*card|voucher|credit|coupon)",
        r"credit\s+of\s+\$\d+",
        r"free\s+item.*(compensation|trouble|order)"
    ]
    has_authorized_voucher = any(term in clean_policy for term in ["voucher", "gift card", "store credit", "compensation"]) and "no " not in clean_policy

    for sentence in sentences:
        s_lower = sentence.lower()
        for trig in compensation_triggers:
            if re.search(trig, s_lower) and not has_authorized_voucher:
                if sentence not in suspicious_statements:
                    suspicious_statements.append(sentence)
                    reasons.append("Offers monetary compensation or vouchers not permitted under company policy.")
                break

    # 4. Immediate Replacement without Prerequisite Checks
    replacement_triggers = [
        r"(dispatched|sending|sent|ship).*replacement.*(immediately|today|right\s+now|without)",
        r"replacement.*(immediately|today|right\s+now)",
        r"new\s+(unit|item|product|one)\s+is\s+on\s+its\s+way\s+(today|immediately|right\s+now)",
        r"replacement\s+will\s+ship\s+today"
    ]
    replacement_conditional = any(term in clean_policy for term in ["return of original", "inspection", "verify defect", "warehouse"])

    for sentence in sentences:
        s_lower = sentence.lower()
        for trig in replacement_triggers:
            if re.search(trig, s_lower) and (replacement_conditional or "immediately" not in clean_policy):
                if sentence not in suspicious_statements:
                    suspicious_statements.append(sentence)
                    reasons.append("Promises an instant replacement without satisfying inspection/return eligibility.")
                break

    detected = len(suspicious_statements) > 0
    if detected:
        explanation = f"Detected {len(suspicious_statements)} unauthorized promise(s): " + " ".join(reasons)
    else:
        explanation = "No unauthorized commitments or false promises were detected in the response."

    return {
        "detected": detected,
        "false_promise_detected": "Yes" if detected else "No",
        "suspicious_statements": suspicious_statements,
        "explanation": explanation
    }
