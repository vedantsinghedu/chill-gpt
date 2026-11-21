"""
Policy Validator Module for ChillGPT.
Evaluates AI-generated customer support responses against company policies.
"""

import re
from typing import Dict, List, Any


def validate_policy(
    customer_complaint: str,
    company_policy: str,
    generated_response: str
) -> Dict[str, Any]:
    """
    Compares the generated response against company policy in context of the customer complaint.

    Args:
        customer_complaint: The customer's grievance text.
        company_policy: The authoritative company terms and conditions.
        generated_response: The support agent/AI drafted response.

    Returns:
        dict: {
            "compliance_status": "Compliant" | "Partially Compliant" | "Non-Compliant",
            "violations": List[str],
            "unsupported_claims": List[str],
            "explanation": str
        }
    """
    violations: List[str] = []
    unsupported_claims: List[str] = []

    clean_complaint = (customer_complaint or "").strip()
    clean_policy = (company_policy or "").strip()
    clean_response = (generated_response or "").strip()

    # Edge Case: Empty generated response
    if not clean_response:
        return {
            "compliance_status": "Non-Compliant",
            "violations": ["Generated response is empty; no customer resolution was provided."],
            "unsupported_claims": [],
            "explanation": "A blank response fails customer support requirements and cannot be policy-compliant."
        }

    # Edge Case: Unclear or missing policy
    if not clean_policy or len(clean_policy.split()) < 4:
        unsupported_claims.append("Company policy is unspecified, empty, or too brief for full validation.")
        return {
            "compliance_status": "Partially Compliant",
            "violations": [],
            "unsupported_claims": unsupported_claims,
            "explanation": "Validation was limited because the company policy is missing or incomplete."
        }

    policy_lower = clean_policy.lower()
    resp_lower = clean_response.lower()
    comp_lower = clean_complaint.lower()

    # Rule 1: "No Refund" or "Final Sale" policy violation
    no_refund_pattern = r"(no\s+(\w+\s+)?refunds?|non-refundable|non\s+refundable|all\s+sales\s+(are\s+)?(strictly\s+)?final|sales\s+are\s+final|cannot\s+be\s+refunded)"
    if re.search(no_refund_pattern, policy_lower):
        refund_promise_pattern = r"(refund|money\s+back|credit\s+your\s+(card|account)|reimburse)"
        if re.search(refund_promise_pattern, resp_lower):
            violations.append("Response promises a refund, directly violating the 'no refunds/final sale' policy.")

    # Rule 2: Return window check
    policy_window_match = re.search(r"(\d+)\s*[- ]*(day|days|calendar days)\s*(return|replacement|refund|exchange|policy)", policy_lower)
    if policy_window_match:
        allowed_days = int(policy_window_match.group(1))
        complaint_days_match = re.search(r"(\d+)\s*[- ]*(day|days)\s*(ago|after|later|since|past)", comp_lower)
        if complaint_days_match:
            claimed_days = int(complaint_days_match.group(1))
            if claimed_days > allowed_days:
                return_promised = re.search(r"(return|refund|exchange|send it back|accept your return)", resp_lower)
                if return_promised:
                    violations.append(
                        f"Order elapsed time ({claimed_days} days) exceeds company return window ({allowed_days} days), "
                        f"yet the response approved a return/refund."
                    )

    # Rule 3: Immediate refund without inspection/receipt/verification
    inspection_required = re.search(r"(inspection|inspect|verified|verification|original receipt|proof of purchase|unboxing video|warehouse receives?|return first)", policy_lower)
    if inspection_required:
        instant_refund = re.search(
            r"((immediate(ly)?|instant(ly)?|right\s+now|today).*refund|refund.*(immediate(ly)?|instant(ly)?|right\s+now|today)|(processed|issued).*refund.*to\s+your\s+(card|account)|money\s+back\s+today)",
            resp_lower
        )
        if instant_refund and "Response promises a refund, directly violating" not in " ".join(violations):
            violations.append(
                "Response promises an immediate/instant refund before the mandatory inspection or verification required by policy."
            )

    # Rule 4: Immediate replacement without return or inspection
    replacement_restricted = re.search(r"replacement\s+(only\s+after|requires|upon|subject\s+to)|replace.*(after\s+return|inspection|verified)", policy_lower)
    if replacement_restricted:
        instant_replacement = re.search(
            r"((dispatched|sending|sent|ship).*replacement.*(immediately|today|right\s+now|without)|replacement.*(immediately|today|right\s+now)|new\s+(one|unit|item).*on\s+its\s+way\s+(today|right\s+now|immediately))",
            resp_lower
        )
        if instant_replacement:
            violations.append(
                "Response promises an immediate replacement dispatch prior to fulfilling policy return/inspection prerequisites."
            )

    # Rule 5: Unsupported compensation or vouchers
    compensation_promised = re.search(r"(\$\d+|\d+%\s*(discount|off)|gift\s*card|store\s*(credit|voucher)|free\s*(coupon|voucher|item|gift))", resp_lower)
    if compensation_promised:
        no_voucher_policy = re.search(r"(no\s+(\w+\s+)?(vouchers?|gift\s+cards?|cash\s+refunds?|compensation))", policy_lower)
        compensation_allowed = re.search(r"(voucher|store credit|gift card|compensation|coupon)", policy_lower)
        if no_voucher_policy:
            violations.append(
                f"Response offers compensation ('{compensation_promised.group(0)}') contrary to policy prohibiting vouchers/compensation."
            )
        elif not compensation_allowed:
            unsupported_claims.append(
                f"Response offers compensation ('{compensation_promised.group(0)}') not authorized anywhere in company policy."
            )

    # Rule 6: Return shipping guarantee contrary to policy
    if re.search(r"(customer\s+pays?\s+return|buyer\s+(is\s+)?responsible\s+for\s+return|shipping\s+fee\s+is\s+non-refundable)", policy_lower):
        if re.search(r"(free\s+return\s+shipping|we\s+will\s+cover\s+(all\s+)?return|prepaid\s+return\s+label)", resp_lower):
            violations.append(
                "Response promises free return shipping contrary to company policy requiring customer to cover return postage."
            )

    # Rule 7: Unsupported delivery guarantee
    delivery_guarantee = re.search(r"(guarantee.*(arrive|deliver|reach)|will\s+definitely\s+(arrive|deliver|reach)|(arrive|deliver).*(tomorrow|within\s+24\s+hours))", resp_lower)
    if delivery_guarantee:
        if not re.search(r"(guaranteed\s+next[- ]day\s+delivery|overnight\s+guaranteed)", policy_lower):
            unsupported_claims.append(
                "Response guarantees next-day delivery without carrier confirmation or policy backing."
            )

    # Rule 8: Polite deflection with zero actionable resolution
    has_polite_greetings = re.search(r"(thank you|have a nice day|have a wonderful|best regards|warmly|warmest regards|blessed day)", resp_lower)
    has_substance = re.search(r"(order|investigat|help|assist|check|step|resolve|tracking|photo|receipt|packing slip|verif)", resp_lower)
    if has_polite_greetings and not has_substance:
        unsupported_claims.append("Response is superficially polite but offers zero substantive resolution to the complaint.")

    # Determine compliance status
    if violations:
        status = "Non-Compliant"
        explanation = f"Detected {len(violations)} direct policy violation(s). The response contradicts explicit operational rules."
    elif unsupported_claims:
        status = "Partially Compliant"
        explanation = f"Response is largely aligned but contains {len(unsupported_claims)} unsupported claim(s) or ambiguities."
    else:
        status = "Compliant"
        explanation = "The response adheres to company policy requirements with no unauthorized claims detected."

    return {
        "compliance_status": status,
        "violations": violations,
        "unsupported_claims": unsupported_claims,
        "explanation": explanation
    }
