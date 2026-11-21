"""
Tone and Professionalism Analyzer Module for ChillGPT.
Evaluates AI-generated customer responses across 5 dimensions:
Professionalism, Empathy, Politeness, Clarity, Customer-Friendliness (1-10).
"""

import re
from typing import Dict, List, Any


def analyze_tone(generated_response: str) -> Dict[str, Any]:
    """
    Evaluates the generated customer support response across 5 tone dimensions.

    Args:
        generated_response: The draft response text.

    Returns:
        dict: {
            "scores": {
                "professionalism": int,      # 1-10
                "empathy": int,              # 1-10
                "politeness": int,           # 1-10
                "clarity": int,              # 1-10
                "customer_friendliness": int # 1-10
            },
            "tone_assessment": str,
            "suggestions": List[str]
        }
    """
    clean_text = (generated_response or "").strip()

    # Edge Case: Empty response
    if not clean_text:
        return {
            "scores": {
                "professionalism": 1,
                "empathy": 1,
                "politeness": 1,
                "clarity": 1,
                "customer_friendliness": 1
            },
            "tone_assessment": "The response is completely empty. No support or communication was provided.",
            "suggestions": [
                "Draft a complete response containing an empathetic greeting, clear solution, and professional sign-off."
            ]
        }

    text_lower = clean_text.lower()
    words = clean_text.split()
    word_count = len(words)

    # Base scores
    prof = 7
    emp = 5
    pol = 6
    clar = 7
    friend = 6
    suggestions: List[str] = []

    # 1. Professionalism Checks
    has_greeting = bool(re.search(r"^(dear|hello|hi|good (morning|afternoon|evening))\b", text_lower))
    has_signoff = bool(re.search(r"(best regards|sincerely|warm regards|warmly|kind regards|support team|customer care)\b", text_lower))
    has_slang = bool(re.search(r"\b(gonna|wanna|lol|idk|btw|bro|dude|yolo|nope|yep|nah)\b", text_lower))
    all_caps_words = [w for w in words if len(w) >= 4 and w.isupper() and w.isalpha()]
    has_shouting = len(all_caps_words) >= 2
    has_hostility = bool(re.search(r"\b(shut up|not my problem|stop complaining|your fault|whatever|leave us alone)\b", text_lower))

    if has_greeting:
        prof += 1
    else:
        prof -= 1
        suggestions.append("Add a courteous opening greeting (e.g., 'Hello [Customer Name],').")

    if has_signoff:
        prof += 1
    else:
        prof -= 1
        suggestions.append("Include a formal support sign-off (e.g., 'Warm regards, Customer Support Team').")

    if has_slang:
        prof -= 3
        suggestions.append("Eliminate informal slang/colloquialisms to maintain business-appropriate language.")

    if has_shouting:
        prof -= 2
        clar -= 1
        suggestions.append("Avoid writing in all-caps, which can come across as aggressive shouting.")

    if has_hostility:
        prof = max(1, prof - 5)
        emp = max(1, emp - 5)
        pol = max(1, pol - 5)
        friend = max(1, friend - 5)
        suggestions.append("Remove hostile, accusatory, or defensive statements immediately.")

    if word_count < 8:
        prof -= 2
        clar -= 2

    # 2. Empathy Checks
    has_empathetic_apology = bool(
        re.search(
            r"(understand (how|your)|sincerely apologize|truly sorry|deeply regret|regret the inconvenience|frustrat|disappoint)",
            text_lower
        )
    )
    has_blame = bool(re.search(r"(you should have|it is your fault|your mistake|you failed to)", text_lower))

    if has_empathetic_apology:
        emp += 3
        friend += 1
    else:
        emp -= 2
        suggestions.append("Acknowledge the customer's frustration and offer a sincere, empathetic apology for the inconvenience.")

    if has_blame:
        emp -= 3
        pol -= 2
        friend -= 2
        suggestions.append("Avoid shifting blame onto the customer; focus constructively on resolving the matter.")

    # 3. Politeness Checks
    courtesy_terms = len(re.findall(r"\b(please|thank you|thanks|kindly|appreciate|grateful)\b", text_lower))
    if courtesy_terms >= 2:
        pol += 2
    elif courtesy_terms == 1:
        pol += 1
    else:
        pol -= 1
        suggestions.append("Use courteous markers like 'please', 'kindly', and 'thank you for your patience'.")

    # 4. Clarity Checks
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
    has_action_steps = bool(re.search(r"(\bplease\s+(reply|provide|send|confirm)|\bstep\s*\d|•|- |\d+\.)", text_lower))

    if has_action_steps:
        clar += 1
    if len(sentences) >= 2:
        clar += 1
    # Check for run-on sentences
    long_sentences = [s for s in sentences if len(s.split()) > 35]
    if long_sentences:
        clar -= 2
        suggestions.append("Break long, dense sentences into shorter, structured paragraphs or bullet points for readability.")

    # 5. Customer-Friendliness Checks
    supportive_language = bool(
        re.search(
            r"(here to help|happy to assist|rest assured|work together|glad to help|reach out anytime)",
            text_lower
        )
    )
    if supportive_language:
        friend += 2
    if emp >= 7 and pol >= 7:
        friend += 1

    # Clamp all scores between 1 and 10
    scores = {
        "professionalism": max(1, min(10, prof)),
        "empathy": max(1, min(10, emp)),
        "politeness": max(1, min(10, pol)),
        "clarity": max(1, min(10, clar)),
        "customer_friendliness": max(1, min(10, friend))
    }

    # Generate holistic tone assessment
    avg_score = sum(scores.values()) / 5.0
    if avg_score >= 8.0:
        tone_assessment = (
            "Excellent tone. The response is polished, courteous, empathetic, and aligns well "
            "with modern e-commerce customer support standards."
        )
    elif avg_score >= 5.5:
        tone_assessment = (
            "Adequate tone, but lacks emotional warmth and empathetic engagement. "
            "It resolves the operational point but could feel robotic or transactional to an upset customer."
        )
    else:
        tone_assessment = (
            "Substandard tone. The response lacks basic customer care standards, displays defensive "
            "or blunt diction, and risks escalating customer dissatisfaction."
        )

    # Deduplicate suggestions
    unique_suggestions = []
    for sug in suggestions:
        if sug not in unique_suggestions:
            unique_suggestions.append(sug)

    if not unique_suggestions:
        unique_suggestions.append("Maintain the current tone standards; response is clear, respectful, and empathetic.")

    return {
        "scores": scores,
        "tone_assessment": tone_assessment,
        "suggestions": unique_suggestions
    }
