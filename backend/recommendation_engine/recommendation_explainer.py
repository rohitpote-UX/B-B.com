"""
Brand Battle — Recommendation Explainability Engine
Generates human-readable explanations detailing why products were recommended.
"""

from typing import List, Dict, Any, Optional
from models import Product


class RecommendationExplainer:
    """Produces multi-signal human-readable explanation strings and metadata badges."""

    def build_explanation(
        self, 
        rec_type: str, 
        candidate: Product, 
        baseline_product: Optional[Product] = None,
        score: float = 0.0,
        extra_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesize explainability components into a structured explanation object."""
        bullet_points = []
        badge = "Recommended"

        if extra_reason:
            bullet_points.append(extra_reason)

        if rec_type == "better_alternatives":
            badge = "Better Choice"
            bullet_points.append("Higher overall performance and user satisfaction rating")
            if candidate.average_rating:
                bullet_points.append(f"Rated {candidate.average_rating}/5.0 by verified buyers")

        elif rec_type == "budget_alternatives":
            badge = "Budget Save"
            if baseline_product and baseline_product.current_best_price and candidate.current_best_price:
                savings_pct = int(((baseline_product.current_best_price - candidate.current_best_price) / baseline_product.current_best_price) * 100)
                bullet_points.append(f"{savings_pct}% lower cost than flagship baseline")

        elif rec_type == "premium_upgrades":
            badge = "Premium Upgrade"
            bullet_points.append("Superior hardware build and enhanced display/camera specs")

        elif rec_type == "best_value":
            badge = "Best Value"
            if candidate.deal_score:
                bullet_points.append(f"Top Deal Score of {int(candidate.deal_score)}/100 across major marketplaces")

        elif rec_type == "trending":
            badge = "Trending"
            bullet_points.append("High browsing momentum and surge in search demand this week")

        elif rec_type == "similar_specs":
            badge = "Spec Match"
            bullet_points.append(f"Over 90% hardware specification overlap with requested item")

        elif rec_type == "accessories":
            badge = "Essential Accessory"
            bullet_points.append("Frequently purchased together as a complementary addon")

        if not bullet_points:
            bullet_points.append("Matched based on Knowledge Graph relationships and user preferences")

        return {
            "type": rec_type,
            "badge": badge,
            "primary_reason": bullet_points[0],
            "explanation_points": bullet_points,
            "confidence_percentage": int(score * 100) if score <= 1.0 else int(score)
        }
