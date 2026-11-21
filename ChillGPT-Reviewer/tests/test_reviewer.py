"""
Test Suite: Reviewer Coordinator & Public API Contract
ChillGPT — Part 2
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from modules.response_reviewer import review_response


def test_review_response_returns_all_required_keys():
    """Verifies that review_response returns the exact structured keys required by Part 1."""
    complaint = "My order #552 arrived broken."
    policy = "Defective items eligible for replacement within 7 days upon photo verification."
    response = (
        "Hello! We apologize for the broken item on order #552. Please send a photo of the damage "
        "and we will send a replacement. Warm regards, ChillGPT Team."
    )

    result = review_response(complaint, policy, response)

    expected_keys = [
        "compliance_status",
        "policy_violations",
        "false_promises",
        "missing_information",
        "tone_scores",
        "tone_assessment",
        "improvement_suggestions",
        "improved_response",
    ]

    for key in expected_keys:
        assert key in result, f"Missing required key in result dictionary: {key}"

    assert result["compliance_status"] in ["Compliant", "Partially Compliant", "Non-Compliant"]
    assert isinstance(result["policy_violations"], list)
    assert isinstance(result["false_promises"], dict)
    assert isinstance(result["missing_information"], list)
    assert isinstance(result["tone_scores"], dict)
    assert isinstance(result["tone_assessment"], str)
    assert isinstance(result["improvement_suggestions"], list)
    assert isinstance(result["improved_response"], str)
    assert len(result["improved_response"]) > 20


def test_tone_scores_contain_all_five_metrics_between_1_and_10():
    """Verifies that all 5 tone dimensions are scored strictly between 1 and 10."""
    complaint = "My order has not arrived."
    policy = "Shipping takes 3-5 days."
    response = "Hi, we are checking your order status right now. Thanks for your patience."

    result = review_response(complaint, policy, response)
    tone_scores = result["tone_scores"]

    required_metrics = ["professionalism", "empathy", "politeness", "clarity", "customer_friendliness"]
    for metric in required_metrics:
        assert metric in tone_scores, f"Missing tone metric: {metric}"
        val = tone_scores[metric]
        assert isinstance(val, (int, float))
        assert 1 <= val <= 10, f"Tone score {metric}={val} is outside allowed range 1-10"


def test_deterministic_fallback_mode_flag():
    """Verifies that when no valid API key is present, analysis_mode marks deterministic fallback."""
    complaint = "Item arrived scratched."
    policy = "Exchanges within 14 days."
    response = "Please send a photo and we will assist."

    # Explicitly pass empty API key
    result = review_response(complaint, policy, response, api_key="")

    assert result["analysis_mode"] == "deterministic_fallback"
    assert "Deterministic" in result["engine_details"]
