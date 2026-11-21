"""
ChillGPT - Module Interface: Part 2 Handoff & Teammate Integration
==============================================================================
IMPORTANT NOTE FOR TEAMMATE (PART 2 DEVELOPER):
This file defines the official data contract and integration hook for
Part 2: Review and Validation Module.

Your module will receive the 'DraftResponseHandoff' package created below,
containing:
1. The original customer complaint
2. The company policy
3. The structured analysis (sentiment, category, details, grounding)
4. The chosen tone
5. The generated draft response from Part 1
==============================================================================
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json


class DraftResponseHandoff:
    """
    Standardized payload created by Part 1 and passed to Part 2 for review and validation.
    """

    def __init__(
        self,
        complaint_text: str,
        company_policy: str,
        analysis: Dict[str, Any],
        tone: str,
        draft_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.complaint_text = complaint_text
        self.company_policy = company_policy
        self.analysis = analysis
        self.tone = tone
        self.draft_response = draft_response
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.status = "AWAITING_PART2_REVIEW"
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert handoff package to a serializable dictionary."""
        return {
            "status": self.status,
            "created_at": self.created_at,
            "complaint_text": self.complaint_text,
            "company_policy": self.company_policy,
            "analysis": self.analysis,
            "tone": self.tone,
            "draft_response": self.draft_response,
            "metadata": self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Export as formatted JSON."""
        return json.dumps(self.to_dict(), indent=indent)


class ReviewerModuleInterface:
    """
    Abstract / base interface reserved for the Part 2 teammate.
    Your teammate should inherit from this class when implementing their module.
    """

    def validate_draft(self, handoff: DraftResponseHandoff) -> Dict[str, Any]:
        """
        Validate and review the draft response against policy and complaint.
        To be implemented by teammate in Part 2.
        """
        raise NotImplementedError("Part 2 Review & Validation Module is to be implemented by Teammate.")


def create_handoff_package(
    complaint_text: str,
    company_policy: str,
    analysis: Dict[str, Any],
    tone: str,
    draft_response: str,
    model_name: str = "chillgpt-engine"
) -> DraftResponseHandoff:
    """
    Constructs the official handoff package to be consumed by Part 2.
    """
    return DraftResponseHandoff(
        complaint_text=complaint_text,
        company_policy=company_policy,
        analysis=analysis,
        tone=tone,
        draft_response=draft_response,
        metadata={
            "generator_module": "Part 1: Complaint Analysis & Response Generation",
            "model_engine": model_name,
            "schema_version": "1.0.0"
        }
    )
