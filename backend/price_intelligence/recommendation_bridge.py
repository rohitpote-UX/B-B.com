"""
Brand Battle — Recommendation Bridge Module
Connects Price Intelligence with AI Recommendation Engine and Product Knowledge Graph signals.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product


class RecommendationBridge:
    """Bridge service connecting Price Intelligence with recommendation platform."""

    def get_recommendation_signals(self, db: Session, product_id: int) -> Dict[str, Any]:
        """Fetch recommendation engine signals for a product."""
        try:
            from recommendation_engine import recommendation_orchestrator
            recs = recommendation_orchestrator.get_product_recommendations(db, product_id, limit=3)
            return {
                "has_recommendations": True,
                "top_recommendation_count": len(recs.get("recommendations", [])),
            }
        except Exception:
            return {"has_recommendations": False, "top_recommendation_count": 0}


# Singleton
recommendation_bridge = RecommendationBridge()
