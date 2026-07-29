"""
Brand Battle - Ensemble Confidence Engine
Combines multi-signal scores into an explainable composite match confidence score.
Generates machine-readable and human-readable signal contributions.
"""

from typing import Dict, Any
from matching_engine.matching_config import SIGNAL_WEIGHTS


class ConfidenceEngine:
    """Computes explainable ensemble match confidence from individual signal evaluations."""

    def compute_ensemble_confidence(
        self,
        signals: Dict[str, Dict[str, Any]],
        custom_weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculates weighted composite confidence score (0.0 to 1.0) and detailed signal breakdown.

        `signals` dict should contain keys:
            title_similarity, brand_match, model_token_overlap, semantic_embedding,
            attribute_match, spec_similarity, category_match, price_similarity

        Each signal value must be a dict with at least `score` and `explanation`.
        """
        weights = custom_weights or SIGNAL_WEIGHTS

        # Brand match zero-gating
        brand_signal = signals.get("brand_match", {})
        if brand_signal.get("score", 0.5) == 0.0:
            # Conflicting brands -> overall match fails
            return {
                "ensemble_confidence": 0.0,
                "gated_by": "brand_mismatch",
                "explainability": {
                    "brand_match": {
                        "score": 0.0,
                        "weight": weights.get("brand_match", 0.20),
                        "contribution": 0.0,
                        "explanation": brand_signal.get("explanation", "Brand mismatch gate")
                    }
                },
                "summary_reason": "Hard gate triggered: Conflicting brand identity"
            }

        total_weight = 0.0
        weighted_score_sum = 0.0
        breakdown = {}

        for signal_name, weight in weights.items():
            sig_data = signals.get(signal_name, {})
            score = sig_data.get("score", 0.5)
            explanation = sig_data.get("explanation", "Signal evaluated")

            contribution = round(score * weight, 4)
            weighted_score_sum += contribution
            total_weight += weight

            breakdown[signal_name] = {
                "score": round(score, 3),
                "weight": round(weight, 3),
                "contribution": round(contribution, 4),
                "explanation": explanation,
            }

        final_confidence = round(weighted_score_sum / total_weight, 3) if total_weight > 0 else 0.0
        final_confidence = min(1.0, max(0.0, final_confidence))

        summary = f"Composite confidence {final_confidence:.3f} from {len(breakdown)} signals"

        return {
            "ensemble_confidence": final_confidence,
            "gated_by": None,
            "explainability": breakdown,
            "summary_reason": summary
        }


confidence_engine = ConfidenceEngine()
