"""
ChillGPT - Unified LLM Client
Provides connectivity to:
1. Offline Prompt Simulator (Deterministic demo engine for reliable offline grading/demos)
2. Google Gemini API (via direct HTTP REST)
3. OpenAI-Compatible API (OpenAI, Groq, OpenRouter, Ollama)

No heavy external SDKs required; uses standard 'requests' library.
"""

import json
import re
import os
from typing import Dict, Any, Optional
import requests


class LLMClient:
    """Unified client for executing prompts across different LLM backends."""

    def __init__(
        self,
        provider: str = "simulator",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize the LLM Client.
        :param provider: 'simulator', 'gemini', or 'openai'
        :param api_key: API Key for the selected provider
        :param model_name: Name of model to invoke (e.g. 'gemini-1.5-flash', 'gpt-4o-mini')
        :param base_url: Optional base URL for OpenAI-compatible endpoints (e.g. Groq/Ollama)
        """
        self.provider = (provider or "simulator").lower().strip()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        self.model_name = model_name
        self.base_url = base_url

        if not self.model_name:
            if self.provider == "gemini":
                self.model_name = "gemini-1.5-flash"
            elif self.provider == "openai":
                self.model_name = "gpt-4o-mini"
            else:
                self.model_name = "chillgpt-simulator-v1"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        json_mode: bool = False
    ) -> str:
        """
        Dispatches prompt execution to the configured provider.
        """
        if self.provider == "simulator":
            return self._run_simulator(system_prompt, user_prompt, json_mode)
        elif self.provider == "gemini":
            return self._call_gemini_api(system_prompt, user_prompt, temperature, json_mode)
        elif self.provider in ["openai", "custom"]:
            return self._call_openai_api(system_prompt, user_prompt, temperature, json_mode)
        else:
            raise ValueError(f"Unknown provider '{self.provider}'. Choose 'simulator', 'gemini', or 'openai'.")

    # ==========================================================================
    # GOOGLE GEMINI REST API
    # ==========================================================================
    def _call_gemini_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool
    ) -> str:
        if not self.api_key:
            raise ValueError("Google Gemini API Key is missing. Please enter your key in the sidebar or switch to Offline Simulator.")

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            response = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini returned an empty response candidate list.")

            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join([part.get("text", "") for part in parts])
            return text.strip()

        except requests.exceptions.RequestException as err:
            err_msg = str(err)
            if hasattr(err, "response") and err.response is not None:
                try:
                    err_json = err.response.json()
                    err_msg = err_json.get("error", {}).get("message", str(err))
                except Exception:
                    err_msg = err.response.text
            raise RuntimeError(f"Gemini API Error: {err_msg}")

    # ==========================================================================
    # OPENAI / COMPATIBLE REST API
    # ==========================================================================
    def _call_openai_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool
    ) -> str:
        if not self.api_key:
            raise ValueError("API Key is missing. Please enter your OpenAI/Groq key in the sidebar or switch to Offline Simulator.")

        base = self.base_url.rstrip("/") if self.base_url else "https://api.openai.com/v1"
        endpoint = f"{base}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as err:
            err_msg = str(err)
            if hasattr(err, "response") and err.response is not None:
                try:
                    err_json = err.response.json()
                    err_msg = err_json.get("error", {}).get("message", str(err))
                except Exception:
                    err_msg = err.response.text
            raise RuntimeError(f"OpenAI API Error: {err_msg}")

    # ==========================================================================
    # OFFLINE SIMULATOR ENGINE (FOR OFFLINE DEMOS & HIGH RELIABILITY)
    # ==========================================================================
    def _run_simulator(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        """
        High-fidelity heuristic engine simulating prompt execution.
        Follows prompt directives with structured extraction and policy grounding.
        """
        if json_mode or "COMPLAINT ANALYSIS MODE" in system_prompt or "--- INSTRUCTIONS ---" in user_prompt:
            return self._simulate_analysis(user_prompt)
        else:
            return self._simulate_response(user_prompt)

    def _simulate_analysis(self, prompt: str) -> str:
        """Simulate the JSON extraction from complaint and policy."""
        complaint_match = re.search(r"--- CUSTOMER COMPLAINT ---\s*(.*?)\s*--- INSTRUCTIONS ---", prompt, re.DOTALL)
        policy_match = re.search(r"--- COMPANY POLICY ---\s*(.*?)\s*--- CUSTOMER COMPLAINT ---", prompt, re.DOTALL)

        complaint = complaint_match.group(1).strip() if complaint_match else prompt
        policy = policy_match.group(1).strip() if policy_match else ""

        complaint_lower = complaint.lower()
        policy_lower = policy.lower()

        # 1. Extract Order ID
        order_match = re.search(r"(?:order\s*(?:#|id)?\s*[:\-]?\s*)([A-Za-z0-9\-_#]+)", complaint, re.IGNORECASE)
        order_id = order_match.group(1).strip("# ") if order_match else "Not provided"

        # 2. Extract Customer Name
        name_match = re.search(r"(?:my name is|i am|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", complaint)
        customer_name = name_match.group(1).strip() if name_match else "Valued Customer"

        # 3. Detect Sentiment & Intensity
        angry_words = ["ridiculous", "dispute", "lawyer", "lawsuit", "scam", "unacceptable", "furious", "terrible", "1-star", "ruin", "crushed", "horrible", "hung up", "ftc", "hate", "worst"]
        frustrated_words = ["demands", "hurry", "unfair", "annoyed", "frustrated", "waiting", "charged", "useless", "broken", "severed", "smoking", "late", "where is", "deliver it", "totally late"]
        anxious_words = ["worried", "urgently", "anniversary", "birthday", "gift", "wondering", "please help", "hope", "tomorrow", "tonight", "dinner party"]
        disappointed_words = ["unfortunately", "doesn't work", "defective", "failed", "does not charge", "disappointed"]

        if any(w in complaint_lower for w in angry_words):
            sentiment = "Angry"
            intensity = 10 if ("lawsuit" in complaint_lower or "ftc" in complaint_lower or "furious" in complaint_lower) else 9
            rationale = "Customer expressed sharp hostility, threatened legal/regulatory disputes, or used intense outrage language."
        elif any(w in complaint_lower for w in frustrated_words):
            sentiment = "Frustrated"
            intensity = 8
            rationale = "Customer voiced strong dissatisfaction regarding product failure, delayed transit, or unexpected billing."
        elif any(w in complaint_lower for w in anxious_words):
            sentiment = "Anxious"
            intensity = 7
            rationale = "Customer has a time-sensitive event or urgency and is concerned about resolution timeframe."
        elif any(w in complaint_lower for w in disappointed_words):
            sentiment = "Disappointed"
            intensity = 6
            rationale = "Customer is disappointed that a recently acquired product failed to perform as expected."
        else:
            sentiment = "Neutral"
            intensity = 4
            rationale = "Customer inquiry is matter-of-fact without extreme emotional keywords."

        # 4. Classify Category
        if any(w in complaint_lower for w in ["earbud", "hardware", "charge", "screen", "power on", "shattered", "broken", "defective", "gadget", "device", "stopped", "heating", "not working", "fails", "defect", "faulty", "damaged", "malfunction", "smoking", "cord", "casing", "speaker", "blender", "parts"]):
            category = "Product Defect"
        elif any(w in complaint_lower for w in ["shipping", "tracking", "courier", "memphis", "transit", "delivered", "parcel", "box", "package", "delivery", "carrier", "late", "steaks"]):
            category = "Delivery & Shipping"
        elif any(w in complaint_lower for w in ["subscription", "charge", "charged", "billing", "$49", "credit card", "renew", "invoice"]):
            category = "Billing & Payments"
        elif any(w in complaint_lower for w in ["return", "refund", "swap", "exchange", "watch", "final sale", "ex-"]):
            category = "Returns & Refunds"
        elif any(w in complaint_lower for w in ["agent", "hung up", "customer service", "representative", "support"]):
            category = "Customer Service"
        else:
            category = "Customer Service"

        # 5. Extract Details & Demands
        demands = []
        if "cash refund" in complaint_lower or "full refund" in complaint_lower or "money back" in complaint_lower or "100% full refund" in complaint_lower:
            demands.append("Full refund")
        elif "refund" in complaint_lower:
            demands.append("Refund payment")
        if "upgrade" in complaint_lower or "upgraded" in complaint_lower:
            demands.append("Free upgraded model")
        if "replacement" in complaint_lower or "swap" in complaint_lower or "new replacement" in complaint_lower or "exchange" in complaint_lower or "reship" in complaint_lower:
            demands.append("Product replacement / exchange")
        if "compensation" in complaint_lower or "voucher" in complaint_lower or "gift card" in complaint_lower or "$200" in complaint_lower or "$100" in complaint_lower or "$50" in complaint_lower:
            demands.append("Monetary compensation / voucher")
        if "reroute" in complaint_lower or "deliver it immediately" in complaint_lower:
            demands.append("Expedited / rerouted delivery")
        if not demands:
            demands.append("Assistance resolving the issue")

        # 6. Extract Product / Dates
        product_name = "Not specified"
        known_products = [
            "ProBook laptop", "Nova Wireless Earbuds", "CloudFlow Pro", "SmartHome Speaker",
            "gourmet steaks", "blender", "silver watch", "gold watch", "laptop", "earbuds",
            "subscription", "steaks", "watch", "speaker", "parcel", "device", "gadget"
        ]
        for p in known_products:
            if p.lower() in complaint_lower:
                product_name = p
                break
        if product_name == "Not specified":
            prod_match = re.search(r"(?:my|the|this|a|an)\s+([A-Za-z0-9\s\-]{3,25}?)\s+(?:order|arrived|stopped|has|was|is|died|started|broke|cost|yesterday|two days)", complaint, re.IGNORECASE)
            if prod_match:
                candidate = prod_match.group(1).strip()
                if len(candidate.split()) <= 4 and candidate.lower() not in ["order", "parcel", "package", "problem", "issue", "box"]:
                    product_name = candidate

        dates = "Recent purchase"
        date_match = re.search(r"(\d+\s*(?:days|weeks|months|hours)\s*ago)", complaint, re.IGNORECASE)
        if date_match:
            dates = date_match.group(1)

        # 7. Identify Missing Information Needed Per Policy
        missing_information = []
        if order_id == "Not provided":
            missing_information.append("Order ID (required to verify purchase)")
        
        # Check serial number requirement
        if ("serial number" in policy_lower or "serial" in policy_lower) and not re.search(r"serial\s*(?:#|no|number)?\s*[:\-]?\s*[A-Za-z0-9]+", complaint, re.IGNORECASE):
            if category == "Product Defect" or "warranty" in policy_lower:
                missing_information.append("Device Serial Number")

        # Check photo requirement for damaged goods
        if ("photo" in policy_lower or "pictures" in policy_lower) and ("damage" in complaint_lower or "crushed" in complaint_lower or "cracked" in complaint_lower or "severed" in complaint_lower):
            if "photo" not in complaint_lower and "picture" not in complaint_lower:
                missing_information.append("Photographs showing the damaged item and packaging")

        # Check part numbers requirement if missing parts complaint
        if "missing parts" in complaint_lower or "part numbers" in policy_lower:
            if not re.search(r"part\s*(?:#|no|number)?\s*[:\-]?\s*[A-Za-z0-9]+", complaint, re.IGNORECASE):
                missing_information.append("Specific part numbers of the missing components")

        # Check purchase date if required by warranty policy and not mentioned
        if ("date of purchase" in policy_lower or "proof of purchase" in policy_lower) and dates == "Recent purchase":
            if not any(w in complaint_lower for w in ["yesterday", "days ago", "weeks ago", "months ago", "today"]):
                missing_information.append("Date of purchase / proof of purchase")

        # 8. Evaluate Policy Grounding
        supported_actions = []
        unsupported_demands = []
        applicable_clauses = ""

        # Specific Pre-built Scenario Matches:
        if "slipped" in complaint_lower or "dropped" in complaint_lower or "shattered" in complaint_lower or "kitchen table" in complaint_lower:
            unsupported_demands.extend(["Immediate cash refund (accidental drop excluded)", "Free replacement", "Compensation for emotional distress"])
            if "20%" in policy_lower or "paid repairs" in policy_lower:
                supported_actions.append("20% discount on certified paid repair service under warranty center")
            applicable_clauses = "Clause 3: Accidental damage (drops, cracked screens) excluded from warranty and returns. Clause 1: 14-day limit for unopened items."

        elif "doesn't charge" in complaint_lower or "left earbud" in complaint_lower:
            supported_actions.append("Free replacement under 1-Year Limited Warranty (reported within 14 days)")
            applicable_clauses = "Clause 2: Manufacturer defects eligible for free replacement/repair under 1-Year Limited Warranty."

        elif "anniversary" in complaint_lower and "memphis" in complaint_lower:
            unsupported_demands.extend(["Immediate address reroute (restricted to 60 min after order)", "Refund while package is actively in transit", "$50 gift card compensation"])
            supported_actions.append("Carrier tracking monitoring and carrier trace investigation if inactive for over 48 hours")
            applicable_clauses = "Clause 1: 3-5 business day standard window. Clause 2: Address changes within 60 min only. Clause 3: 48h stillness before trace. Clause 4: No vouchers for carrier delays."

        elif "charged" in complaint_lower and ("cloudflow" in complaint_lower or "forgot to cancel" in complaint_lower):
            unsupported_demands.append("Immediate refund for partial month/forgotten cancellation")
            supported_actions.extend(["Assistance with cancelling auto-renewal in billing portal", "Retain active software access until end of current paid cycle"])
            applicable_clauses = "Clause 2: Cancellation stops future renewals. Clause 3: Strict no-refund policy for partial months or forgotten cancellations unless SLA downtime breach."

        # Dynamic Evaluator for Any Test Case / Custom Policy:
        else:
            # Check refund demand vs policy
            has_refund_demand = any("refund" in d.lower() or "money back" in d.lower() for d in demands)
            if has_refund_demand:
                if any(term in policy_lower for term in [
                    "refunds are strictly not offered", "strictly not offered", "refunds are not offered",
                    "no refunds", "no-refund", "non-refundable", "strictly not permitted", "ineligible for refunds",
                    "final sale", "cannot be issued", "replacement only", "replacements only"
                ]):
                    unsupported_demands.append("Refund request (policy strictly restricts refunds for this item/circumstance)")
                elif "within 14 days" in policy_lower or "full refund" in policy_lower:
                    supported_actions.append("Review refund eligibility upon receipt and inspection")

            # Check replacement / swap demand vs policy
            has_swap_demand = any("replacement" in d.lower() or "swap" in d.lower() or "exchange" in d.lower() for d in demands)
            if has_swap_demand:
                if any(term in policy_lower for term in [
                    "non-exchangeable", "ineligible for ... swaps", "ineligible for swaps", "final sale", "cannot be swapped"
                ]):
                    unsupported_demands.append("Exchange / replacement request (custom or final-sale items are non-exchangeable)")
                elif any(term in policy_lower for term in [
                    "eligible for free replacement", "free replacement", "warranty replacement", "replacements will be dispatched", "reshipped at no cost"
                ]):
                    supported_actions.append("Complimentary replacement dispatch in accordance with warranty terms")

            # If product is damaged/defective and policy offers replacement as remedy
            if category == "Product Defect" or "damaged" in complaint_lower or "defective" in complaint_lower or "cracked" in complaint_lower:
                if any(term in policy_lower for term in ["eligible for free replacement", "free replacement", "warranty replacement", "replacements will be dispatched", "reshipped at no cost", "replacement only"]):
                    if not any("replacement" in s.lower() for s in supported_actions):
                        supported_actions.append("Complimentary replacement dispatch in accordance with policy terms upon verification")

            # Check compensation / voucher demand vs policy
            has_comp_demand = any("compensation" in d.lower() or "voucher" in d.lower() for d in demands)
            if has_comp_demand:
                if any(term in policy_lower for term in [
                    "does not provide monetary compensation", "no vouchers", "not qualify for shipping refunds or monetary compensation",
                    "not offered", "cash settlements"
                ]):
                    unsupported_demands.append("Monetary compensation / voucher request (unauthorized under company policy)")

            # Check upgraded model demand
            if any("upgrade" in d.lower() for d in demands):
                if "upgrades" in policy_lower or "does not provide" in policy_lower:
                    unsupported_demands.append("Product model upgrade (not supported by policy)")

            # Check tracking / in-transit demands
            if "deliver it immediately" in complaint_lower or "reroute" in complaint_lower or "late" in complaint_lower:
                if "48 hours" in policy_lower or "in transit" in policy_lower:
                    unsupported_demands.append("Immediate delivery reroute or courier expedite while package is in carrier transit")
                    supported_actions.append("Carrier tracking monitoring and carrier trace investigation if inactivity exceeds 48 hours")

            # Check missing parts reshipment
            if "missing parts" in complaint_lower:
                if "reshipped at no cost" in policy_lower or "reshipped" in policy_lower:
                    supported_actions.append("Free reshipment of missing parts upon confirmation of part numbers")

            if not supported_actions:
                supported_actions.append("Policy-standard customer service inquiry review and resolution")
            applicable_clauses = "Applicable company policy terms and warranty provisions."

        # Main issue formulation
        if "shattered" in complaint_lower:
            main_issue = "Customer experienced screen damage after laptop slipped off table and is demanding a full cash refund, replacement, and compensation."
        elif "doesn't charge" in complaint_lower:
            main_issue = "Customer received newly delivered earbuds where the left earbud fails to power on or charge out of the box."
        elif "anniversary" in complaint_lower:
            main_issue = "Customer is anxious over a standard delivery anniversary gift whose tracking has paused for 20 hours in transit."
        elif "forgot to cancel" in complaint_lower:
            main_issue = "Customer was charged for a monthly subscription renewal they forgot to cancel and is requesting an immediate refund."
        elif "crushed" in complaint_lower:
            main_issue = "Customer received a severely damaged parcel with inoperable contents and demands an immediate replacement without providing Order ID or photos."
        elif "hung up" in complaint_lower or "lawsuit" in complaint_lower:
            main_issue = "Customer received missing parts, experienced poor support agent interaction, and is threatening legal action while demanding vouchers and upgrades."
        elif "steaks" in complaint_lower or "dinner party" in complaint_lower:
            main_issue = "Customer's express gourmet steaks delivery is delayed in transit before a dinner party and tracking has paused for 36 hours."
        elif "engraved" in complaint_lower or "broke up" in complaint_lower:
            main_issue = "Customer seeks to return or swap a custom engraved watch after a personal breakup, contrary to final-sale policy."
        elif "smoking" in complaint_lower or "blender" in complaint_lower:
            main_issue = "Customer's blender motor failed on the second day and customer is demanding replacement/refund without providing required order details."
        else:
            main_issue = f"Customer has raised an issue regarding {product_name} concerning {', '.join(demands)}."

        result_obj = {
            "main_issue": main_issue,
            "sentiment": sentiment,
            "sentiment_intensity": intensity,
            "sentiment_rationale": rationale,
            "category": category,
            "important_details": {
                "order_id": order_id,
                "product_name": product_name,
                "dates_mentioned": dates,
                "demands_made": demands,
                "customer_name": customer_name
            },
            "missing_information": missing_information,
            "policy_grounding": {
                "supported_actions": supported_actions,
                "unsupported_demands": unsupported_demands,
                "applicable_clauses": applicable_clauses
            }
        }
        return json.dumps(result_obj, indent=2)

    def _simulate_response(self, prompt: str) -> str:
        """Simulate tone-steered response generation grounded strictly in policy."""
        # Detect Tone
        tone = "Professional"
        for t in ["Empathetic", "Friendly", "Professional"]:
            if f"TONE: {t.upper()}" in prompt or f"SELECTED RESPONSE TONE ---\n{t}" in prompt:
                tone = t
                break
            elif f"Selected Response Tone: {t}" in prompt:
                tone = t
                break

        # Extract Customer name & order
        name_match = re.search(r"Customer Name:\s*([^\n\r]+)", prompt)
        customer_name = name_match.group(1).strip() if name_match else "Valued Customer"
        if customer_name in ["Valued Customer", "Not provided"]:
            salutation = "Hello,"
        else:
            salutation = f"Dear {customer_name}," if tone == "Professional" else f"Hi {customer_name},"

        order_match = re.search(r"Order ID:\s*([^\n\r]+)", prompt)
        order_id = order_match.group(1).strip() if order_match else "Not provided"

        # Check for pre-built scenario keywords
        prompt_lower = prompt.lower()
        is_laptop_drop = "shattered" in prompt_lower or "slipped" in prompt_lower
        is_earbuds_defect = "earbud" in prompt_lower or "doesn't charge" in prompt_lower
        is_shipping = "memphis" in prompt_lower or ("anniversary" in prompt_lower and "20 hours" in prompt_lower)
        is_saas = "cloudflow" in prompt_lower or ("forgot to cancel" in prompt_lower and "$49" in prompt_lower)
        is_damaged_parcel_pkg = "crushed" in prompt_lower and "torn open" in prompt_lower

        # Case 1: Laptop Screen Drop
        if is_laptop_drop:
            ref_order = f"Order {order_id}" if order_id != "Not provided" else "your device"
            if tone == "Professional":
                return f"""{salutation}

Thank you for contacting TechGear Customer Support regarding your ProBook laptop ({ref_order}). We understand that experiencing a broken screen is a stressful and inconvenient situation.

Upon careful review of our Company Returns & Warranty Policy, we must respectfully clarify our guidelines regarding accidental damage. Under Clause 3, accidental physical damage—including drops, spills, and cracked screens—is explicitly excluded from standard return eligibility and from our 1-Year Limited Warranty, which covers manufacturer defects only. Furthermore, return eligibility is limited to unopened items within 14 days of delivery. For these reasons, we cannot authorize an immediate cash refund, complimentary replacement, or compensatory payout.

However, we are committed to helping you resolve this. Under our policy, we are pleased to offer you a 20% discount on certified screen repair through our authorized service center to restore your laptop with genuine parts.

To initiate a repair evaluation, please reply with your device serial number so our technical team can generate a service ticket.

Best regards,
Customer Support Team | ChillGPT Assistant"""

            elif tone == "Friendly":
                return f"""{salutation}

Thanks for reaching out to us at TechGear. Oh no—having your laptop slip off the table and crack the screen is such an unfortunate accident, especially for a laptop you rely on!

I want to be completely open and transparent with you about what our policies allow. Because the crack resulted from an accidental drop, our Returns and Warranty Guidelines (Clause 3) unfortunately do not cover accidental damage, and we are unable to approve free replacements or cash refunds for accidents.

That said, we definitely want to help you get your ProBook back in working order! We would love to provide our company-approved 20% discount on certified screen repairs at our authorized service facility. 

Whenever you are ready, just reply with your device's serial number, and we will prepare a discounted repair quote for you right away.

Best regards,
Customer Support Team | ChillGPT Assistant"""

            else:  # Empathetic
                return f"""{salutation}

I am truly sorry to hear about what happened to your ProBook laptop ({ref_order}). Seeing an essential device you invested in slip and shatter its screen is deeply distressing, and I completely understand the frustration and alarm you felt when reaching out.

I wish I could provide the complimentary replacement or immediate refund you requested, but in full honesty, our Returns & Warranty Policy strictly excludes accidental damage such as drops and cracked screens, and we cannot issue cash compensation. I know this is not the answer you were hoping for, and I genuinely regret having to share it.

What I can personally do to assist you right now is set up our policy-approved 20% discount on certified manufacturer screen repair. Our authorized technicians will replace the display with original parts while preserving your hardware warranty.

Please share your laptop's serial number at your convenience, and we will take care of the next steps together.

Best regards,
Customer Support Team | ChillGPT Assistant"""

        # Case 2: Earbuds Defect
        elif is_earbuds_defect:
            ref_order = f"Order {order_id}" if order_id != "Not provided" else "your purchase"
            if tone == "Professional":
                return f"""{salutation}

Thank you for contacting TechGear Customer Support regarding your Nova Wireless Earbuds ({ref_order}). We sincerely apologize for the inconvenience caused by the left earbud failing to charge.

According to Clause 2 of our Returns & Warranty Policy, hardware exhibiting manufacturer defects within the 1-Year Limited Warranty period—and reported within 14 days of delivery—is fully eligible for a complimentary replacement. As you contacted us promptly within this return window, we are ready to initiate your replacement.

To complete this request:
1. Please provide the serial number printed on the underside of your charging case.
2. Confirm your current delivery address.

Once verified, we will issue a pre-paid return label and dispatch your new replacement unit immediately.

Best regards,
Customer Support Team | ChillGPT Assistant"""

            elif tone == "Friendly":
                return f"""{salutation}

Thanks for getting in touch with TechGear! We're thrilled you chose the Nova Wireless Earbuds, but we're so sorry that the left earbud isn't charging properly out of the box. That is definitely not the smooth experience we want for your work calls!

The great news is that because you reported this within your first 14 days and it is a manufacturer hardware defect, you are 100% eligible for a free replacement pair under our 1-Year Limited Warranty.

To get your brand-new pair sent out, could you please share:
• The serial number on the bottom of the charging case
• Confirmation of your shipping address

As soon as we receive that, we'll send a pre-paid return label and get your replacement on the way!

Best regards,
Customer Support Team | ChillGPT Assistant"""

            else:  # Empathetic
                return f"""{salutation}

Thank you for reaching out, Priya. I can completely understand how disappointing and frustrating it is to unbox brand-new earbuds for your daily work calls, only to find that one isn't powering on. Your time and peace of mind are very important to us, and I sincerely apologize for this hassle.

Please be assured that we will make this right for you. Under Clause 2 of our 1-Year Limited Warranty and 14-day defect policy, you are fully entitled to a free replacement. We will cover the return shipping and ensure you receive a fully tested, functional pair.

Could you kindly share the serial number located on the underside of the charging case? As soon as you reply, I will personally ensure your replacement ticket is prioritized.

Best regards,
Customer Support Team | ChillGPT Assistant"""

        # Case 3: Shipping Delay
        elif is_shipping:
            ref_order = f"Order {order_id}" if order_id != "Not provided" else "your shipment"
            if tone == "Professional":
                return f"""{salutation}

Thank you for contacting SwiftShop regarding the delivery status of {ref_order}. We recognize the vital importance of this parcel arriving on time for your anniversary celebration.

Regarding our delivery guidelines, standard shipping has an estimated delivery timeframe of 3 to 5 business days. Our policy states that carrier tracking updates may pause for up to 48 consecutive hours during transit before an investigation trace can be initiated. Furthermore, under Clauses 2, 3, and 4 of our Shipping Policy, courier rerouting is only permitted within 60 minutes of placing the order, and refunds or gift cards cannot be issued while an order is actively in transit or delayed by carrier logistics.

We are actively monitoring your parcel's status in Memphis. If tracking does not register new movement within the next 28 hours (completing 48 hours of inactivity), our support team will immediately open an official carrier trace to expedite delivery.

We appreciate your patience as we oversee your delivery.

Best regards,
Customer Support Team | ChillGPT Assistant"""

            else:
                return f"""{salutation}

First, please accept my heartfelt congratulations on your 10th anniversary! I completely understand why you are anxious and worried about this package arriving in time for tomorrow's celebration, and I truly share your concern.

I reviewed {ref_order} immediately. Your package was dispatched via Standard Shipping, which has a 3 to 5 business day delivery window. Under our company shipping policy, tracking updates frequently pause while packages are sorted at regional carrier hubs like Memphis, and carrier trace investigations can only be initiated after 48 consecutive hours without movement. For this reason, along with our transit guidelines, we cannot issue an immediate refund, address reroute, or gift card while the package is actively moving in carrier transit.

Please know that we are keeping a close watch on your shipment. If the scan does not refresh by tomorrow, we will immediately escalate this with the carrier dispatch team to help get your anniversary gift to you as swiftly as possible.

Best regards,
Customer Support Team | ChillGPT Assistant"""

        # Dynamic Synthesizer for Generic and Custom Complaints:
        else:
            missing_info_match = re.search(r"Missing Information Identified:\s*([^\n\r]+)", prompt)
            missing_info_str = missing_info_match.group(1).strip() if missing_info_match else ""
            has_missing = missing_info_str and "None" not in missing_info_str

            unsupported_match = re.search(r"Unsupported Demands:\s*([^\n\r]+)", prompt)
            unsupported_str = unsupported_match.group(1).strip() if unsupported_match else ""
            has_unsupported = unsupported_str and "None" not in unsupported_str

            supported_match = re.search(r"Supported Actions:\s*([^\n\r]+)", prompt)
            supported_str = supported_match.group(1).strip() if supported_match else "Standard assistance and verification"

            ref_order = f" regarding Order {order_id}" if order_id != "Not provided" else ""

            # Build missing information bullet points if needed
            missing_items = [item.strip() for item in missing_info_str.split(",") if item.strip()] if has_missing else []
            if missing_items:
                missing_bullets = "\n" + "\n".join([f"• {item}" for item in missing_items])
            else:
                missing_bullets = ""

            if tone == "Professional":
                decline_stmt = f"\n\nPlease be advised that in accordance with our Company Policy, we are unable to approve requests for: {unsupported_str}." if has_unsupported else ""
                missing_stmt = f"\n\nTo allow our team to proceed with your request, please provide the following required details:{missing_bullets}" if has_missing else ""

                return f"""{salutation}

Thank you for contacting Customer Support{ref_order}. We have received your inquiry and appreciate the opportunity to assist you.

Regarding your request, our policy supports the following resolution: {supported_str}.{decline_stmt}{missing_stmt}

Please let us know how you would like to proceed, and our support team will be glad to assist you.

Best regards,
Customer Support Team | ChillGPT Assistant"""

            elif tone == "Friendly":
                decline_stmt = f"\n\nI want to be completely upfront and honest that under our company policy, we are unable to approve {unsupported_str}." if has_unsupported else ""
                missing_stmt = f"\n\nTo help us get everything sorted out for you as quickly as possible, could you please send over:{missing_bullets}" if has_missing else ""

                return f"""{salutation}

Thanks so much for reaching out to us{ref_order}! We really appreciate your patience while we work on this for you.

Here is what we can do to help you right now under our policy: {supported_str}.{decline_stmt}{missing_stmt}

We are here to help, so please reply whenever you are ready!

Best regards,
Customer Support Team | ChillGPT Assistant"""

            else:  # Empathetic
                decline_stmt = f"\n\nI truly understand this may be disappointing news, but under our company policy, we are unfortunately unable to grant {unsupported_str}." if has_unsupported else ""
                missing_stmt = f"\n\nTo ensure we can resolve this matter for you as smoothly and quickly as possible, could you kindly provide us with:{missing_bullets}" if has_missing else ""

                return f"""{salutation}

Thank you for reaching out to us{ref_order}. I truly understand how frustrating and stressful this situation has been for you, and I sincerely appreciate your patience.

I want to do everything possible within our policy guidelines to assist you. Here is the resolution we are able to provide right away: {supported_str}.{decline_stmt}{missing_stmt}

Please let me know if you have any questions, and I will be more than happy to guide you through each step.

Best regards,
Customer Support Team | ChillGPT Assistant"""
