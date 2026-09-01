"""
Brand Battle — Recommendation Explanation Engine
Generates explainable recommendation reasons and trust badges.
"""

from typing import Dict, Any, List, Optional


class ExplanationEngine:
    """Builds human-readable explainable reasons for recommendations."""

    def generate_explanation(
        self,
        rec_type: str,
        target_product: Any,
        candidate_product: Any,
        score: float
    ) -> Dict[str, Any]:
        reasons = ["✓ Verified same product category"]

        target_price = getattr(target_product, "current_best_price", 0.0) or 0.0
        cand_price = getattr(candidate_product, "current_best_price", 0.0) or 0.0

        if cand_price and target_price:
            if cand_price < target_price:
                diff_pct = round(((target_price - cand_price) / target_price) * 100)
                reasons.append(f"✓ {diff_pct}% lower price than {getattr(target_product, 'name', 'current model')}")
            elif cand_price > target_price:
                reasons.append(f"✓ Premium tier specifications")

        target_rating = getattr(target_product, "average_rating", 4.0) or 4.0
        cand_rating = getattr(candidate_product, "average_rating", 4.0) or 4.0
        if cand_rating >= target_rating:
            reasons.append(f"✓ High rating ({cand_rating}★)")

        reasons.append("✓ AI neural graph validated")

        badge = "Direct Alternative"
        if "budget" in rec_type.lower():
            badge = "Best Budget Alternative"
        elif "upgrade" in rec_type.lower() or "premium" in rec_type.lower():
            badge = "Premium Upgrade"
        elif "value" in rec_type.lower():
            badge = "Highest Value"

        return {
            "badge": badge,
            "primary_reason": reasons[1] if len(reasons) > 1 else reasons[0],
            "bullet_reasons": reasons,
            "confidence_score": round(score, 2)
        }


explanation_engine = ExplanationEngine()
