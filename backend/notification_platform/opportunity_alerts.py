"""
Brand Battle — 7. Opportunity Alerts Engine
Notifies users when Opportunity Score exceeds a high threshold (>85/100).
"""

from typing import Dict, Any, Optional
from models import Product


class OpportunityAlertsEngine:
    """Generates high-priority Opportunity Notifications."""

    def generate_opportunity_alert(
        self, product: Product, opportunity_score: float
    ) -> Optional[Dict[str, Any]]:
        """Generate alert when Opportunity Score > 85/100."""
        if opportunity_score < 85.0:
            return None

        return {
            "title": f"🔥 Exceptional Deal Opportunity: {product.name}",
            "body": (
                f"Opportunity Score reached {opportunity_score:.0f}/100. "
                "Today is one of the best buying opportunities seen for this product in the last six months."
            ),
            "opportunity_score": opportunity_score,
            "product_id": product.id,
        }


# Singleton
opportunity_alerts_engine = OpportunityAlertsEngine()
