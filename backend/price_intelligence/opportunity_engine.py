"""
Brand Battle — 18. Opportunity Score Engine
Proprietary Brand Battle metric (0-100) combining price, forecast, discount, marketplace, alternatives, popularity, and volatility.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.buy_confidence import buy_confidence_engine
from price_intelligence.fake_discount_detector import fake_discount_detector


class OpportunityScoreEngine:
    """Computes master Brand Battle Opportunity Score (0-100)."""

    def calculate_opportunity_score(self, db: Session, product: Product) -> float:
        """Calculate master Brand Battle Opportunity Score."""
        confidence = buy_confidence_engine.calculate_confidence(db, product)
        fv = fair_value_engine.calculate_fair_value(db, product)
        discount_audit = fake_discount_detector.audit_discount(db, product)

        # Baseline score from buy confidence
        base_score = confidence

        # Underpriced bonus / Overpriced penalty
        if fv.underpriced_percentage > 0:
            price_factor = min(20.0, fv.underpriced_percentage * 1.5)
        else:
            price_factor = -min(30.0, fv.overpriced_percentage * 1.5)

        # Fake discount penalty
        if discount_audit.is_manipulated:
            penalty = discount_audit.fake_discount_pct * 1.2
        else:
            penalty = 0.0

        final_score = round(base_score + price_factor - penalty, 1)
        return min(100.0, max(0.0, final_score))


# Singleton
opportunity_engine = OpportunityScoreEngine()
