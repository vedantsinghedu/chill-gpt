"""
Dedicated Test Suite for ChillGPT - Part 1: Complaint Analysis & Response Generation
Covers the 5 required test cases:
1. Damaged product with refund request.
2. Late delivery complaint.
3. Angry customer demanding compensation.
4. Customer complaint with missing order details.
5. Complaint where company policy clearly does not allow the requested refund or replacement.
"""

import unittest
from modules.llm_client import LLMClient
from modules.analyzer import ComplaintAnalyzer
from modules.generator import ResponseGenerator
from modules.reviewer_interface import create_handoff_package


class TestPart1FiveRequiredCases(unittest.TestCase):

    def setUp(self):
        self.client = LLMClient(provider="simulator")
        self.analyzer = ComplaintAnalyzer(llm_client=self.client)
        self.generator = ResponseGenerator(llm_client=self.client)

    # --------------------------------------------------------------------------
    # Case 1: Damaged product with refund request
    # --------------------------------------------------------------------------
    def test_case_1_damaged_product_refund_request(self):
        complaint = (
            "I received my SmartHome Speaker (Order #SH-40912) two days ago, but the power cord is severed "
            "and the casing is cracked. I want an immediate full refund to my credit card."
        )
        policy = (
            "SMARTHOME POLICY: Defective or transit-damaged items reported within 7 days of delivery are "
            "eligible for free replacement only. Refunds are strictly not offered for opened or damaged items; "
            "replacements will be dispatched upon receipt of photos showing the damage and serial number."
        )

        analysis = self.analyzer.analyze(complaint, policy)
        self.assertEqual(analysis["category"], "Product Defect")
        self.assertIn(analysis["sentiment"], ["Frustrated", "Disappointed", "Angry"])
        self.assertIn("SH-40912", analysis["important_details"]["order_id"])

        # Check policy grounding
        grounding = analysis["policy_grounding"]
        self.assertTrue(
            any("refund" in u.lower() for u in grounding["unsupported_demands"]),
            "Refund demand should be flagged as unsupported since policy offers replacement only."
        )
        self.assertTrue(
            any("replacement" in s.lower() for s in grounding["supported_actions"]),
            "Replacement should be identified as supported action."
        )

        # Check missing info
        self.assertTrue(
            any("photo" in m.lower() for m in analysis["missing_information"]) or
            any("serial" in m.lower() for m in analysis["missing_information"]),
            "Missing photos or serial number should be identified."
        )

        # Response verification
        for tone in ["Professional", "Friendly", "Empathetic"]:
            resp = self.generator.generate_response(complaint, policy, analysis, tone=tone)
            self.assertIn("SH-40912", resp)
            self.assertTrue(
                "unable to" in resp.lower() or "cannot" in resp.lower() or "not offered" in resp.lower() or "restricts refunds" in resp.lower(),
                f"Response in {tone} tone should adhere to policy and decline refund."
            )
            # Response must NOT promise refund
            self.assertNotIn("issue a full refund", resp.lower())
            self.assertNotIn("we have refunded", resp.lower())

        print("\n✅ Case 1 Passed: Damaged product with refund request (Refund declined, replacement offered, missing photos requested).")

    # --------------------------------------------------------------------------
    # Case 2: Late delivery complaint
    # --------------------------------------------------------------------------
    def test_case_2_late_delivery_complaint(self):
        complaint = (
            "Where is my order #FD-55102? I ordered gourmet steaks 4 days ago with 2-day Express Delivery. "
            "The tracking hasn't moved in 36 hours. I needed this for a dinner party tonight and it is totally late! Deliver it immediately!"
        )
        policy = (
            "FRESHDELIVERY SHIPPING POLICY: Express delivery delivers in 2-3 business days. If tracking does not update "
            "for over 48 hours, support will initiate a carrier trace investigation. Carrier delays due to transit sorting "
            "are not eligible for shipping refunds or cancellations while in transit. Customers must provide tracking/Order ID."
        )

        analysis = self.analyzer.analyze(complaint, policy)
        self.assertEqual(analysis["category"], "Delivery & Shipping")
        self.assertIn(analysis["sentiment"], ["Anxious", "Frustrated", "Angry"])
        self.assertIn("FD-55102", analysis["important_details"]["order_id"])

        # Grounding check
        grounding = analysis["policy_grounding"]
        self.assertTrue(
            any("inactivity exceeds 48 hours" in s.lower() or "trace" in s.lower() for s in grounding["supported_actions"])
        )

        # Response verification
        for tone in ["Professional", "Friendly", "Empathetic"]:
            resp = self.generator.generate_response(complaint, policy, analysis, tone=tone)
            self.assertIn("FD-55102", resp)
            self.assertTrue(
                "trace" in resp.lower() or "monitoring" in resp.lower() or "48 hours" in resp.lower(),
                f"Response in {tone} tone should explain tracking/trace policy."
            )

        print("✅ Case 2 Passed: Late delivery complaint (Carrier trace policy explained, grounded expectation set).")

    # --------------------------------------------------------------------------
    # Case 3: Angry customer demanding compensation
    # --------------------------------------------------------------------------
    def test_case_3_angry_customer_demanding_compensation(self):
        complaint = (
            "Order #AB-99210 arrived with missing parts. Your customer service agent hung up on me earlier! "
            "I am furious. I demand an immediate $200 compensation voucher plus a free upgraded model or I am filing a lawsuit and reporting you to the FTC!"
        )
        policy = (
            "APEXBUILD SUPPORT POLICY: Missing parts reported within 30 days will be reshipped at no cost with standard shipping. "
            "ApexBuild does not provide monetary compensation, vouchers, cash settlements, or product upgrades for support escalations. "
            "Order ID and part numbers must be provided."
        )

        analysis = self.analyzer.analyze(complaint, policy)
        self.assertEqual(analysis["sentiment"], "Angry")
        self.assertEqual(analysis["sentiment_intensity"], 10)

        # Check that compensation and upgrade demands were identified as disallowed
        unsupported = analysis["policy_grounding"]["unsupported_demands"]
        self.assertTrue(
            any("compensation" in u.lower() or "voucher" in u.lower() for u in unsupported),
            "Compensation demand should be marked unsupported."
        )
        self.assertTrue(
            any("upgrade" in u.lower() for u in unsupported),
            "Upgrade demand should be marked unsupported."
        )

        # Check response de-escalates and declines unauthorized items
        resp = self.generator.generate_response(complaint, policy, analysis, tone="Empathetic")
        self.assertTrue(
            "unable to" in resp.lower() or "not provide" in resp.lower() or "cannot" in resp.lower(),
            "Response must politely decline compensation and upgrade."
        )
        self.assertNotIn("$200 voucher has been approved", resp.lower())
        self.assertNotIn("we will send an upgraded model", resp.lower())

        print("✅ Case 3 Passed: Angry customer demanding compensation (De-escalated, compensation/upgrade declined, parts reshipment offered).")

    # --------------------------------------------------------------------------
    # Case 4: Customer complaint with missing order details
    # --------------------------------------------------------------------------
    def test_case_4_missing_order_details(self):
        complaint = (
            "My blender started smoking and died on the second day. I want my money back or a replacement. Send someone to fix this ASAP."
        )
        policy = (
            "KITCHENPRO POLICY: 1-Year Limited Warranty covers motor defects. Customer must provide Order ID, date of purchase, "
            "and serial number located on the base of the blender. Unauthorized repairs void warranty. Eligible items receive free warranty replacement."
        )

        analysis = self.analyzer.analyze(complaint, policy)
        self.assertEqual(analysis["category"], "Product Defect")
        self.assertEqual(analysis["important_details"]["order_id"], "Not provided")

        # Must flag missing details
        missing = analysis["missing_information"]
        self.assertTrue(
            any("order id" in m.lower() for m in missing),
            "Missing Order ID must be flagged."
        )
        self.assertTrue(
            any("serial" in m.lower() for m in missing),
            "Missing serial number must be flagged."
        )

        # Generated response must explicitly request the missing information
        resp = self.generator.generate_response(complaint, policy, analysis, tone="Professional")
        self.assertTrue(
            "order id" in resp.lower() or "details" in resp.lower(),
            "Response must ask customer for missing Order ID."
        )
        self.assertTrue(
            "serial" in resp.lower() or "number" in resp.lower(),
            "Response must ask customer for missing serial number."
        )

        print("✅ Case 4 Passed: Complaint with missing order details (Order ID and serial number identified and requested).")

    # --------------------------------------------------------------------------
    # Case 5: Policy clearly does not allow requested refund or replacement
    # --------------------------------------------------------------------------
    def test_case_5_policy_disallows_refund_or_replacement(self):
        complaint = (
            "I bought a custom engraved silver watch (Order #WT-11883) 3 weeks ago for my ex. We broke up so I don't want it anymore. "
            "I want to return it for a 100% full refund or swap it for a men's gold watch."
        )
        policy = (
            "LUXEWATCH RETURN POLICY: Standard watches may be returned within 14 days of receipt. Custom engraved, personalized, "
            "or resized watches are strictly FINAL SALE and are non-returnable, non-exchangeable, and ineligible for refunds or swaps under any circumstances."
        )

        analysis = self.analyzer.analyze(complaint, policy)
        self.assertEqual(analysis["category"], "Returns & Refunds")

        # Must identify refund and swap as strictly disallowed
        unsupported = analysis["policy_grounding"]["unsupported_demands"]
        self.assertTrue(
            any("refund" in u.lower() for u in unsupported),
            "Refund must be identified as unsupported for final sale watch."
        )
        self.assertTrue(
            any("exchange" in u.lower() or "swap" in u.lower() or "replacement" in u.lower() for u in unsupported),
            "Swap/exchange must be identified as unsupported for final sale watch."
        )

        # Response must decline both
        for tone in ["Professional", "Friendly", "Empathetic"]:
            resp = self.generator.generate_response(complaint, policy, analysis, tone=tone)
            self.assertIn("WT-11883", resp)
            self.assertTrue(
                "unable to" in resp.lower() or "cannot" in resp.lower() or "not able" in resp.lower(),
                f"Response in {tone} tone must decline refund and swap."
            )
            # Must NOT promise refund or swap
            self.assertNotIn("we will issue a refund", resp.lower())
            self.assertNotIn("we can swap", resp.lower())

        print("✅ Case 5 Passed: Disallowed refund/replacement (Final sale policy upheld, refund and swap declined courteously).")

    # --------------------------------------------------------------------------
    # Handoff Contract Integrity
    # --------------------------------------------------------------------------
    def test_handoff_contract_integrity(self):
        complaint = "Test complaint text"
        policy = "Test policy text"
        analysis = self.analyzer.analyze(complaint, policy)
        draft = self.generator.generate_response(complaint, policy, analysis, tone="Professional")

        pkg = create_handoff_package(complaint, policy, analysis, "Professional", draft)
        data = pkg.to_dict()

        self.assertEqual(data["status"], "AWAITING_PART2_REVIEW")
        self.assertEqual(data["complaint_text"], complaint)
        self.assertEqual(data["company_policy"], policy)
        self.assertEqual(data["draft_response"], draft)
        self.assertIn("metadata", data)
        print("✅ Handoff Contract Verified: Part 2 integration seam is intact and ready.")


if __name__ == "__main__":
    unittest.main()
