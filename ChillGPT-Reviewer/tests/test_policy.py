"""
Test Suite: Policy Compliance, False Promises, and Verification Checks (Scenarios 1-10)
ChillGPT — Part 2
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from modules.response_reviewer import review_response
from modules.policy_validator import validate_policy
from modules.false_promise_detector import detect_false_promises
from modules.information_checker import check_missing_information
from modules.tone_analyzer import analyze_tone


def test_01_fully_policy_compliant_response():
    """TEST-01: Fully policy-compliant response."""
    complaint = "My order #1029 arrived with a broken zipper. I would like a replacement."
    policy = "Damaged items reported within 7 days with Order ID and photographic proof are eligible for replacement."
    response = (
        "Hello! Thank you for reaching out to ChillGPT support. We sincerely apologize for the broken zipper on your order #1029. "
        "Could you please share a clear photograph of the defect? Once received, we will inspect it and issue a prepaid return label and replacement. "
        "Warm regards, ChillGPT Support Team."
    )

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Compliant"
    assert len(result["policy_violations"]) == 0
    assert result["false_promises"]["detected"] is False
    assert result["false_promises"]["false_promise_detected"] == "No"


def test_02_response_promising_unauthorised_refund():
    """TEST-02: Response promising an unauthorised refund contrary to policy."""
    complaint = "I don't like the color of the shoes I bought. Give me my money back immediately."
    policy = "All footwear sales are final and non-refundable. Exchanges for defective items only."
    response = (
        "Hello! No problem at all, I have processed a full refund to your card right now. "
        "The money will be in your account today."
    )

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Non-Compliant"
    assert any("refund" in v.lower() for v in result["policy_violations"])
    assert result["false_promises"]["detected"] is True
    assert result["false_promises"]["false_promise_detected"] == "Yes"


def test_03_response_promising_immediate_replacement():
    """TEST-03: Response promising an immediate replacement without prerequisite checks."""
    complaint = "The speaker won't turn on. Send me another one right away."
    policy = "Replacement only after return of original product and warehouse inspection."
    response = (
        "Hi! We are so sorry. We have dispatched a replacement immediately today. "
        "You do not need to send the old one back."
    )

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Non-Compliant"
    assert any("replacement" in v.lower() for v in result["policy_violations"])
    assert result["false_promises"]["detected"] is True


def test_04_response_missing_order_verification_details():
    """TEST-04: Response missing order verification details."""
    complaint = "My package has not arrived and it has been a week! Where is it?"
    policy = "Inquiries regarding delayed shipments require the Order ID and delivery postal code."
    response = (
        "Hello! We are looking into this delay right away. We will let you know once we have an update. "
        "Best regards, Support Team."
    )

    result = review_response(complaint, policy, response)

    missing_items = [m["item"] for m in result["missing_information"]]
    assert any("Order ID" in item for item in missing_items)


def test_05_response_with_unprofessional_tone():
    """TEST-05: Response with an unprofessional tone."""
    complaint = "Why did my delivery get delayed? This is ridiculous."
    policy = "Standard delivery takes 3-5 business days. Agents must maintain a calm and courteous tone."
    response = "Bro, chill out. Stop crying about delays. It is gonna take 5 days, read the website lol."

    result = review_response(complaint, policy, response)

    scores = result["tone_scores"]
    assert scores["professionalism"] <= 5
    assert scores["politeness"] <= 5
    assert len(result["improvement_suggestions"]) > 0


def test_06_response_with_unsupported_delivery_guarantee():
    """TEST-06: Response with an unsupported delivery guarantee."""
    complaint = "Can I get my package by tomorrow afternoon for a birthday party?"
    policy = "Orders are shipped via standard courier within 3-5 business days. No delivery dates are guaranteed."
    response = (
        "Hello! We guarantee that your order will arrive tomorrow morning without fail! "
        "Best regards, Support Team."
    )

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] in ["Partially Compliant", "Non-Compliant"]
    assert result["false_promises"]["detected"] is True
    assert any("tomorrow" in s.lower() for s in result["false_promises"]["suspicious_statements"])


def test_07_response_containing_multiple_policy_violations():
    """TEST-07: Response containing multiple policy violations."""
    complaint = "I received a cracked vase. I am furious!"
    policy = "All sales final. Damaged fragile goods must be inspected before any store credit. No cash refunds or vouchers."
    response = (
        "Hello! We are so sorry. We will refund you immediately right now and also give you a $50 gift card for your trouble! "
        "Plus, we have dispatched a replacement right now!"
    )

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Non-Compliant"
    assert len(result["policy_violations"]) >= 2
    assert result["false_promises"]["detected"] is True


def test_08_response_polite_but_does_not_resolve():
    """TEST-08: Response that is polite but does not resolve the complaint."""
    complaint = "My order arrived missing two items. Please help."
    policy = "Missing items must be reported within 48 hours with order ID and packing slip photo for investigation."
    response = (
        "Dear Customer, Thank you very much for reaching out to us today. We truly appreciate your patronage. "
        "Have a wonderful and blessed day ahead! Warmest regards, Customer Care."
    )

    result = review_response(complaint, policy, response)

    # Should flag missing information and lack of substantive resolution
    missing_items = [m["item"] for m in result["missing_information"]]
    assert any("Order ID" in item for item in missing_items)
    assert result["compliance_status"] in ["Partially Compliant", "Non-Compliant"]


def test_09_empty_generated_response():
    """TEST-09: Empty generated response."""
    complaint = "My package arrived empty!"
    policy = "Report damaged or missing shipments within 3 days."
    response = "   "

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Non-Compliant"
    assert any("empty" in v.lower() for v in result["policy_violations"])
    assert result["tone_scores"]["professionalism"] == 1


def test_10_unclear_or_incomplete_policy():
    """TEST-10: Unclear or incomplete company policy."""
    complaint = "Can I get a refund for my item?"
    policy = "Returns."
    response = "Hello, we can help with your return. Please provide your order details."

    result = review_response(complaint, policy, response)

    assert result["compliance_status"] == "Partially Compliant"
    assert any("policy is unspecified" in v.lower() or "incomplete" in v.lower() for v in result["policy_violations"])
