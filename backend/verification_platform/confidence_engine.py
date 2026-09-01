"""
Brand Battle — Confidence Engine
Calculates individual spec confidence and overall product verification confidence.
"""

from typing import List, Dict, Any
from verification_platform.schemas import SpecConfidence


class ConfidenceEngine:
    """Computes specification and aggregate product verification scores."""

    def compute_product_confidence(self, spec_confidences: List[SpecConfidence]) -> float:
        """
        Calculates overall verification percentage from individual spec confidences.
        """
        if not spec_confidences:
            return 80.0

        scores = [sc.confidence_score for sc in spec_confidences]
        avg_score = sum(scores) / len(scores)
        
        # Penalize if critical specs are unverified or disputed
        disputed_count = sum(1 for sc in spec_confidences if sc.status == "Disputed")
        penalty = disputed_count * 3.5

        final_score = max(0.0, min(100.0, avg_score - penalty))
        return round(final_score, 1)

    def determine_status(self, confidence_score: float, is_disputed: bool) -> str:
        if is_disputed and confidence_score < 80.0:
            return "Disputed"
        if confidence_score >= 85.0:
            return "Verified"
        return "Unverified"


confidence_engine = ConfidenceEngine()
