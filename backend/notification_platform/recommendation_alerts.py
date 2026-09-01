"""
Brand Battle — 9. Personalized Recommendation Alerts Engine
Generates highly curated recommendations matching user budget and style.
"""

from typing import Dict, Any
from models import Product


class RecommendationAlertsEngine:
    """Generates personalized recommendation notifications."""

    def format_recommendation_alert(
        self, product: Product, savings_pct: float, reason: str
    ) -> Dict[str, Any]:
        """Format highly relevant recommendation alert."""
        return {
            "title": f"Recommended for You: {product.name}",
            "body": f"We found an item matching your budget and style—currently {savings_pct:.0f}% below fair market value. {reason}",
            "product_id": product.id,
        }


# Singleton
recommendation_alerts_engine = RecommendationAlertsEngine()
