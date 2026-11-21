"""
Unit tests for ChillGPT - Part 1: Complaint Analysis & Response Generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import unittest
import json
from config import load_sample_policies, load_sample_complaints
from modules.llm_client import LLMClient
from modules.analyzer import ComplaintAnalyzer
from modules.generator import ResponseGenerator
from modules.reviewer_interface import create_handoff_package, DraftResponseHandoff


class TestChillGPTPart1(unittest.TestCase):

    def setUp(self):
        self.client = LLMClient(provider="simulator")
        self.analyzer = ComplaintAnalyzer(llm_client=self.client)
        self.generator = ResponseGenerator(llm_client=self.client)
        self.policies = load_sample_policies()
        self.complaints = load_sample_complaints()

    def test_sample_data_loaded(self):
        self.assertEqual(len(self.policies), 3, "Should have 3 sample policies")
        self.assertEqual(len(self.complaints), 5, "Should have 5 sample complaints")

    def test_complaint_analysis_all_scenarios(self):
        for comp in self.complaints:
            policy_id = comp.get("policy_id")
            matched_policy = next((p for p in self.policies if p["id"] == policy_id), self.policies[0])
            
            analysis = self.analyzer.analyze(
                complaint_text=comp["text"],
                company_policy=matched_policy["text"]
            )

            # Check required fields
            self.assertIn("main_issue", analysis)
            self.assertIn("sentiment", analysis)
            self.assertIn("category", analysis)
            self.assertIn("important_details", analysis)
            self.assertIn("missing_information", analysis)
            self.assertIn("policy_grounding", analysis)

            self.assertGreater(len(analysis["main_issue"]), 5)
            self.assertIn(analysis["sentiment"], ["Angry", "Frustrated", "Disappointed", "Anxious", "Neutral", "Confused"])

        print("\n[Test Success] Analyzed all 5 pre-configured scenarios successfully.")

    def test_missing_information_detection(self):
        # Scenario 5 tests missing Order ID and damaged item photos
        comp_missing = self.complaints[4]
        policy = self.policies[1]["text"]  # SwiftShop

        analysis = self.analyzer.analyze(
            complaint_text=comp_missing["text"],
            company_policy=policy
        )

        self.assertIn("missing_information", analysis)
        missing_items = analysis["missing_information"]
        self.assertGreater(len(missing_items), 0, "Missing info should be detected for scenario 5")

        # Test response generation requests the missing info
        response = self.generator.generate_response(
            complaint_text=comp_missing["text"],
            company_policy=policy,
            analysis_data=analysis,
            tone="Professional"
        )
        self.assertTrue(
            "order id" in response.lower() or "photo" in response.lower(),
            "Generated response should request missing information from customer."
        )
        print("[Test Success] Missing information detected and requested in response.")

    def test_tone_steering_consistency(self):
        comp = self.complaints[0]
        policy = self.policies[0]["text"]
        analysis = self.analyzer.analyze(comp["text"], policy)

        tones = ["Professional", "Friendly", "Empathetic"]
        for tone in tones:
            draft = self.generator.generate_response(
                complaint_text=comp["text"],
                company_policy=policy,
                analysis_data=analysis,
                tone=tone
            )
            self.assertGreater(len(draft), 100)
            # Grounding check: screen drop must decline cash refund
            self.assertTrue(
                "unable to" in draft.lower() or "cannot" in draft.lower() or "do not cover" in draft.lower() or "don't cover" in draft.lower() or "excludes" in draft.lower() or "not covered" in draft.lower(),
                f"Tone {tone} failed policy grounding check: {draft[:100]}"
            )
            print(f"[Test Success] Verified {tone} tone output ({len(draft)} chars)")

    def test_custom_arbitrary_complaint(self):
        custom_complaint = "Hi, I bought a SmartCoffee Maker last week and it stopped heating up. Can someone help me?"
        custom_policy = "SMARTCOFFEE POLICY: 30-day warranty for heating elements. Must provide Order ID and photo of serial tag."

        analysis = self.analyzer.analyze(custom_complaint, custom_policy)
        self.assertEqual(analysis["category"], "Product Defect")
        self.assertIn("order_id", analysis["important_details"])

        draft = self.generator.generate_response(
            complaint_text=custom_complaint,
            company_policy=custom_policy,
            analysis_data=analysis,
            tone="Empathetic"
        )
        self.assertGreater(len(draft), 50)
        print("[Test Success] Custom arbitrary complaint handled dynamically.")

    def test_handoff_package_contract(self):
        comp = self.complaints[1]
        policy = self.policies[0]["text"]
        analysis = self.analyzer.analyze(comp["text"], policy)
        draft = self.generator.generate_response(comp["text"], policy, analysis, tone="Friendly")

        handoff = create_handoff_package(
            complaint_text=comp["text"],
            company_policy=policy,
            analysis=analysis,
            tone="Friendly",
            draft_response=draft
        )

        self.assertIsInstance(handoff, DraftResponseHandoff)
        data_dict = handoff.to_dict()
        self.assertEqual(data_dict["status"], "AWAITING_PART2_REVIEW")
        self.assertEqual(data_dict["tone"], "Friendly")
        self.assertIn("analysis", data_dict)
        self.assertIn("draft_response", data_dict)
        print("[Test Success] Teammate handoff contract verified.")


if __name__ == "__main__":
    unittest.main()
