"""
Test Suite: Edge Cases for Response Reviewer
ChillGPT — Part 2
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from modules.response_reviewer import review_response
from modules.information_checker import check_missing_information


def test_edge_case_01_all_empty_or_whitespace_inputs():
    """EC-01: Empty or whitespace-only inputs across complaint, policy, and response."""
    result = review_response(
        customer_complaint="   \n\t  ",
        company_policy="   ",
        generated_response="   "
    )

    assert result["compliance_status"] == "Non-Compliant"
    assert isinstance(result["policy_violations"], list)
    assert len(result["policy_violations"]) > 0
    assert result["tone_scores"]["professionalism"] == 1
    assert len(result["improved_response"]) > 0


def test_edge_case_02_complaint_already_has_order_id_no_false_missing_flag():
    """EC-02: Customer complaint already provides Order ID and attached photo - should NOT flag as missing."""
    complaint = "My order #99281 arrived broken. I have attached a photo of the cracked glass carafe."
    policy = "Damaged items require Order ID and photo proof within 7 days for exchange."
    response = (
        "Hello! Thank you for contacting us. We received your photo of order #99281. "
        "We are processing your exchange request. Best regards, Support."
    )

    info_result = check_missing_information(complaint, policy, response)

    # Since complaint already contained order #99281 and attached photo, neither should be flagged as missing
    flagged_items = [m["item"] for m in info_result["missing_information"]]
    assert not any("Order ID" in item for item in flagged_items)
    assert not any("Photograph" in item for item in flagged_items)


def test_edge_case_03_massive_verbose_inputs():
    """EC-03: Massive, verbose inputs (stress testing token/text handling)."""
    complaint = "I am writing this long email because my order is late! " * 150  # ~1500 words
    policy = "Deliveries take 3-5 business days. Delays require order ID to track with logistics carrier. " * 30
    response = (
        "Dear Customer, we sincerely apologize for the delay. Could you please provide your Order ID "
        "so we can contact the carrier? Warm regards, Support Team."
    )

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Compliant"
    assert isinstance(result["improved_response"], str)
    assert len(result["improved_response"]) > 10


def test_edge_case_04_slang_emojis_and_informal_text():
    """EC-04: Highly informal text with emojis and slang in response."""
    complaint = "Where's my order at?"
    policy = "Shipping inquiries require order ID."
    response = "Yo fam 💀💀, we gotchu fr fr. Just drop ur order number and we gonna slide into the warehouse."

    result = review_response(complaint, policy, response)

    # Tone analyzer must penalize heavy slang
    assert result["tone_scores"]["professionalism"] < 6
    assert any("slang" in s.lower() for s in result["improvement_suggestions"])


def test_edge_case_05_conflicting_policy_clauses():
    """EC-05: Policy has conflicting terms (e.g., both 7-day return and no refunds)."""
    complaint = "Can I return order #331 for a refund? It has been 5 days."
    policy = "We offer 7-day returns for store credit. All sales are strictly non-refundable and final."
    response = "Hello! Sure, we can issue a full cash refund directly to your credit card right away."

    result = review_response(complaint, policy, response)

    # Response offering cash refund directly violates the non-refundable clause
    assert result["compliance_status"] == "Non-Compliant"
    assert result["false_promises"]["detected"] is True
