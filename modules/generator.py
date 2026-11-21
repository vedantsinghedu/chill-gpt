"""
ChillGPT - Module 1B: Response Generator
Part 1 Component responsible for generating polite, tone-controlled customer support responses
that strictly adhere to the company's policy and extracted complaint analysis.
"""

from typing import Dict, Any, Optional
from .prompts import (
    RESPONSE_SYSTEM_PROMPT,
    RESPONSE_USER_PROMPT,
    TONE_DIRECTIVES
)
from .llm_client import LLMClient


class ResponseGenerator:
    """
    Generates customer support draft responses using prompt engineering.
    Applies:
    - Persona-based response formulation
    - Tone steering (Professional, Friendly, Empathetic)
    - Strict policy grounding (refusing unsupported demands politely)
    - Polite requests for missing required information
    """

    SUPPORTED_TONES = ["Professional", "Friendly", "Empathetic"]

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_response(
        self,
        complaint_text: str,
        company_policy: str,
        analysis_data: Dict[str, Any],
        tone: str = "Professional",
        temperature: float = 0.3
    ) -> str:
        """
        Drafts a grounded response based on complaint, policy, analysis, and selected tone.
        :param complaint_text: Raw complaint text
        :param company_policy: Company policy text
        :param analysis_data: Dictionary returned by ComplaintAnalyzer
        :param tone: One of 'Professional', 'Friendly', 'Empathetic'
        :param temperature: LLM sampling temperature
        :return: Generated response string
        """
        # Validate inputs
        if tone not in self.SUPPORTED_TONES:
            tone = "Professional"

        details = analysis_data.get("important_details", {})
        grounding = analysis_data.get("policy_grounding", {})
        missing_info_list = analysis_data.get("missing_information", [])

        # Extract values for prompt interpolation
        customer_name = details.get("customer_name") or "Valued Customer"
        order_id = details.get("order_id") or "Not provided"
        main_issue = analysis_data.get("main_issue", "Customer inquiry")
        sentiment = analysis_data.get("sentiment", "Frustrated")
        sentiment_intensity = analysis_data.get("sentiment_intensity", 7)
        category = analysis_data.get("category", "General Inquiry")

        unsupported_demands = ", ".join(grounding.get("unsupported_demands", [])) or "None identified"
        supported_actions = ", ".join(grounding.get("supported_actions", [])) or "Standard support guidance"
        applicable_clauses = grounding.get("applicable_clauses", "General policy rules")
        missing_information = ", ".join(missing_info_list) if missing_info_list else "None (all necessary details provided)"

        tone_directive = TONE_DIRECTIVES.get(tone, TONE_DIRECTIVES["Professional"])

        # Format user prompt
        user_prompt = RESPONSE_USER_PROMPT.format(
            policy=company_policy.strip(),
            complaint=complaint_text.strip(),
            customer_name=customer_name,
            main_issue=main_issue,
            sentiment=sentiment,
            sentiment_intensity=sentiment_intensity,
            category=category,
            order_id=order_id,
            missing_information=missing_information,
            unsupported_demands=unsupported_demands,
            supported_actions=supported_actions,
            applicable_clauses=applicable_clauses,
            tone_directive=tone_directive
        )

        # Call LLM client
        response_text = self.llm_client.generate(
            system_prompt=RESPONSE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=temperature,
            json_mode=False
        )

        return response_text.strip()
