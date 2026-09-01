"""
Brand Battle — Verification Models
Defines core model representations for verification records and community submissions.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional


class CommunitySuggestionRecord:
    """Represents a community spec correction submission."""

    def __init__(
        self,
        product_id: int,
        spec_name: str,
        suggested_value: str,
        evidence_url_or_text: str,
        contributor_email: Optional[str] = None
    ):
        self.suggestion_id = f"sug_{uuid.uuid4().hex[:8]}"
        self.product_id = product_id
        self.spec_name = spec_name
        self.suggested_value = suggested_value
        self.evidence_url_or_text = evidence_url_or_text
        self.contributor_email = contributor_email or "anonymous@brandbattle.com"
        self.status = "Pending_Validation"
        self.created_at = datetime.utcnow()
