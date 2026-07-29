"""
Brand Battle - Decision Engine Module
Determines final outcome (AUTO_MATCH, CREATE_NEW_MASTER, ROUTE_TO_REVIEW, MERGE_MASTERS)
based on category-specific confidence thresholds and explainability evaluation.
"""

from typing import Dict, Any, Optional
from matching_engine.matching_config import CATEGORY_THRESHOLDS, THRESHOLD_REVIEW_QUEUE


class MatchingOutcome:
    AUTO_MATCH = "auto_matched"
    CREATE_NEW_MASTER = "create_new"
    ROUTE_TO_REVIEW = "route_review"
    MERGE_MASTERS = "merge_masters"


class DecisionEngine:
    """Evaluates ensemble confidence against category thresholds to select matching outcome."""

    def determine_decision(
        self,
        ensemble_result: Dict[str, Any],
        category: str = "default",
    ) -> Dict[str, Any]:
        """
        Determines the decision outcome based on composite confidence score and category threshold.
        """
        confidence = ensemble_result.get("ensemble_confidence", 0.0)
        gated_by = ensemble_result.get("gated_by")

        # Hard brand mismatch gate
        if gated_by == "brand_mismatch":
            return {
                "decision": MatchingOutcome.CREATE_NEW_MASTER,
                "confidence": 0.0,
                "threshold_used": 0.0,
                "reason": "Brand mismatch hard gate: creating new master product"
            }

        threshold = CATEGORY_THRESHOLDS.get(category, CATEGORY_THRESHOLDS["default"])

        if confidence >= threshold:
            return {
                "decision": MatchingOutcome.AUTO_MATCH,
                "confidence": confidence,
                "threshold_used": threshold,
                "reason": f"Confidence {confidence:.3f} >= category threshold {threshold:.2f} for '{category}'"
            }

        if confidence >= THRESHOLD_REVIEW_QUEUE:
            return {
                "decision": MatchingOutcome.ROUTE_TO_REVIEW,
                "confidence": confidence,
                "threshold_used": THRESHOLD_REVIEW_QUEUE,
                "reason": f"Borderline confidence {confidence:.3f} ({THRESHOLD_REVIEW_QUEUE:.2f} <= score < {threshold:.2f}): routing to review queue"
            }

        return {
            "decision": MatchingOutcome.CREATE_NEW_MASTER,
            "confidence": confidence,
            "threshold_used": threshold,
            "reason": f"Confidence {confidence:.3f} < review threshold {THRESHOLD_REVIEW_QUEUE:.2f}: creating new master product"
        }


decision_engine = DecisionEngine()
