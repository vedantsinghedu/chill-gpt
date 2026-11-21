"""
ChillGPT - Module 1A: Complaint Analyzer
Part 1 Component responsible for extracting key complaint entities, sentiment,
main issues, missing information, and policy-grounding facts.
"""

import json
import re
from typing import Dict, Any, Tuple
from .prompts import ANALYSIS_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT
from .llm_client import LLMClient


class ComplaintAnalyzer:
    """
    Analyzes customer complaints against the company policy.
    Identifies:
    - Main issue
    - Customer sentiment (and emotional intensity)
    - Category of complaint
    - Important details (Order ID, product name, dates, demands)
    - Missing information needed per policy
    - Policy applicability / grounding constraints
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def analyze(self, complaint_text: str, company_policy: str) -> Dict[str, Any]:
        """
        Executes complaint analysis using prompt engineering.
        :param complaint_text: Raw text of customer complaint
        :param company_policy: Text of the company policy
        :return: Parsed structured dictionary
        """
        # Validate inputs
        if not complaint_text or not complaint_text.strip():
            raise ValueError("Customer complaint text cannot be empty.")
        if not company_policy or not company_policy.strip():
            raise ValueError("Company policy text cannot be empty.")

        # Construct prompt
        formatted_user_prompt = ANALYSIS_USER_PROMPT.format(
            complaint=complaint_text.strip(),
            policy=company_policy.strip()
        )

        # Call LLM client
        raw_response = self.llm_client.generate(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            temperature=0.1,  # Low temperature for strict structured extraction
            json_mode=True
        )

        # Parse & sanitize JSON output
        parsed_data = self._clean_and_parse_json(raw_response)

        # Ensure all required fields exist
        validated_data = self._validate_and_normalize(parsed_data, complaint_text)

        return validated_data

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Strip markdown fences, trailing commas, or whitespace from LLM output."""
        cleaned = raw_text.strip()

        # Remove markdown ```json or ``` fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: find first { and last }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                sub_str = cleaned[start:end+1]
                return json.loads(sub_str)
            raise ValueError(f"Failed to parse LLM analysis output as valid JSON: {raw_text[:200]}...")

    def _validate_and_normalize(self, data: Dict[str, Any], raw_complaint: str) -> Dict[str, Any]:
        """Guarantees schema compliance and defaults."""
        normalized = {
            "main_issue": data.get("main_issue") or "Customer reported an operational issue requiring resolution.",
            "sentiment": data.get("sentiment") or "Frustrated",
            "sentiment_intensity": data.get("sentiment_intensity") or 7,
            "sentiment_rationale": data.get("sentiment_rationale") or "Derived from complaint tone and language.",
            "category": data.get("category") or "Customer Service",
            "important_details": data.get("important_details") or {},
            "missing_information": data.get("missing_information") or [],
            "policy_grounding": data.get("policy_grounding") or {}
        }

        # Normalize details
        details = normalized["important_details"]
        if not isinstance(details, dict):
            details = {}
        details.setdefault("order_id", "Not provided")
        details.setdefault("product_name", "Not provided")
        details.setdefault("dates_mentioned", "Recent")
        details.setdefault("demands_made", [])
        details.setdefault("customer_name", "Valued Customer")
        normalized["important_details"] = details

        # Normalize missing information
        if not isinstance(normalized["missing_information"], list):
            normalized["missing_information"] = [str(normalized["missing_information"])] if normalized["missing_information"] else []

        # Normalize policy grounding
        grounding = normalized["policy_grounding"]
        if not isinstance(grounding, dict):
            grounding = {}
        grounding.setdefault("supported_actions", [])
        grounding.setdefault("unsupported_demands", [])
        grounding.setdefault("applicable_clauses", "Standard policy clauses apply.")
        normalized["policy_grounding"] = grounding

        return normalized
