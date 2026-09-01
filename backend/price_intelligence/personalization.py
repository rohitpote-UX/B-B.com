"""
Brand Battle — 20. Personalized Price Intelligence Engine
Personalizes price intelligence alerts, budget alignment, and opportunity scores based on user signals.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product, User


class PersonalizedPriceIntelligenceEngine:
    """Modifies price scoring based on user profile and affinity signals."""

    def personalize_opportunity(
        self, db: Session, product: Product, base_score: float, user_id: Optional[int] = None
    ) -> float:
        """Apply user preference boost to base opportunity score."""
        if not user_id:
            return base_score

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.preferences:
            return base_score

        prefs = user.preferences or {}
        preferred_brands = [b.lower() for b in prefs.get("brands", [])]

        boost = 0.0
        if product.brand and product.brand.name.lower() in preferred_brands:
            boost += 5.0

        return min(100.0, base_score + boost)


# Singleton
personalized_price_engine = PersonalizedPriceIntelligenceEngine()
