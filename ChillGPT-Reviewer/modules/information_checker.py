"""
Information Checker Module for ChillGPT.
Identifies relevant customer details required to resolve a complaint
that the AI-generated response failed to request.
"""

import re
from typing import Dict, List, Any


def check_missing_information(
    customer_complaint: str,
    company_policy: str,
    generated_response: str
) -> Dict[str, Any]:
    """
    Checks if the response fails to request critical information required
    by the complaint type and company policy.

    Args:
        customer_complaint: The customer's grievance text.
        company_policy: Authoritative store policy.
        generated_response: Draft support response.

    Returns:
        dict: {
            "missing_information": List[Dict[str, str]],  # [{"item": "...", "reason": "..."}]
            "explanation": str
        }
    """
    clean_complaint = (customer_complaint or "").strip()
    clean_policy = (company_policy or "").strip().lower()
    clean_response = (generated_response or "").strip()

    if not clean_response:
        return {
            "missing_information": [
                {
                    "item": "Order ID and Customer Verification Details",
                    "reason": "Required to initiate any investigation as the response is empty."
                }
            ],
            "explanation": "No response was generated to collect necessary customer information."
        }

    comp_lower = clean_complaint.lower()
    resp_lower = clean_response.lower()

    missing_items: List[Dict[str, str]] = []

    # 1. Order ID Check
    # Check if complaint already contains an order ID (e.g., #12345, order 1234, id: ORD-99)
    order_id_in_complaint = bool(
        re.search(r"(order\s*#?\s*\d+|#\d+|ord[-_]?\d+|invoice\s*#?\s*\d+)", comp_lower)
    )
    # Check if complaint is about an order-specific issue
    is_order_specific = bool(
        re.search(r"(order|item|package|delivery|shipped|product|bought|purchased|deliver|parcel)", comp_lower)
    )

    if is_order_specific and not order_id_in_complaint:
        # Response should ask for order ID or number
        asked_for_order = bool(
            re.search(r"(order\s*(id|number|#|details)|invoice\s*(number|details)|receipt)", resp_lower)
        )
        if not asked_for_order:
            missing_items.append({
                "item": "Order ID / Invoice Number",
                "reason": "Essential to locate the customer's purchase record and verify purchase date in company systems."
            })

    # 2. Damage / Defect Proof (Photo or Video)
    mentions_damage = bool(
        re.search(r"(damag|broken|crack|shatter|defect|torn|scratched|leaking|stained|faulty|malfunction|dead on arrival)", comp_lower)
    )
    already_attached = bool(
        re.search(r"(attached (a )?(photo|picture|video|image)|see photo|sending pictures)", comp_lower)
    )

    if mentions_damage and not already_attached:
        asked_for_photo = bool(
            re.search(r"(photo|picture|image|video|unboxing\s*(video|footage)|snapshot)", resp_lower)
        )
        if not asked_for_photo:
            missing_items.append({
                "item": "Photograph or Unboxing Video of Damaged Product",
                "reason": "Required by quality assurance and company policy to inspect damage before approving returns or replacements."
            })

    # 3. Delivery / Address / Tracking Verification
    mentions_lost_or_delayed = bool(
        re.search(r"(never arrived|not received|lost|delayed|where is my (package|order)|tracking says delivered)", comp_lower)
    )
    if mentions_lost_or_delayed:
        asked_tracking_or_address = bool(
            re.search(r"(tracking\s*(number|details)|shipping\s*address|delivery\s*address|postal\s*code|pin\s*code)", resp_lower)
        )
        if not asked_tracking_or_address:
            missing_items.append({
                "item": "Shipping Address / Tracking Confirmation",
                "reason": "Required to cross-reference carrier delivery coordinates and initiate an escalation with logistics."
            })

    # 4. Payment / Transaction Details for Billing Disputes
    mentions_billing_dispute = bool(
        re.search(r"(charged twice|double charge|unauthorized charge|bank deduction|overcharged|payment debited)", comp_lower)
    )
    if mentions_billing_dispute:
        asked_payment_details = bool(
            re.search(r"(transaction\s*(id|reference|hash)|bank\s*statement|payment\s*receipt|proof of payment)", resp_lower)
        )
        if not asked_payment_details:
            missing_items.append({
                "item": "Transaction Reference / Bank Deduction Screenshot",
                "reason": "Required to trace the payment gateway transaction and reconcile store ledger records."
            })

    if missing_items:
        explanation = f"Response failed to request {len(missing_items)} critical item(s) needed to resolve the customer complaint."
    else:
        explanation = "The response requested all relevant details required to investigate and resolve the issue."

    return {
        "missing_information": missing_items,
        "explanation": explanation
    }
