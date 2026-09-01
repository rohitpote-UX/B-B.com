"""
Brand Battle — 10. Buy Confidence Score Engine
Aggregates price quality, seller trust, reviews, forecast, warranty, and market alternatives into a master Buy Confidence Score (0-100).
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.fake_discount_detector import fake_discount_detector
from price_intelligence.marketplace_trust import marketplace_trust_engine
from price_intelligence.volatility_engine import volatility_engine
from price_intelligence.config import price_intel_config


class BuyConfidenceScoreEngine:
    """Computes master composite Buy Confidence Score (0-100)."""

    def calculate_confidence(self, db: Session, product: Product) -> float:
        """Compute aggregated Buy Confidence Score."""
        weights = price_intel_config.weights

        # 1. Price Quality Signal (0-100)
        fv = fair_value_engine.calculate_fair_value(db, product)
        if fv.underpriced_percentage > 0:
            price_quality = min(100.0, 70.0 + fv.underpriced_percentage * 2.0)
        else:
            price_quality = max(20.0, 70.0 - fv.overpriced_percentage * 2.0)

        # 2. Historical Discount Trust Signal (0-100)
        discount_audit = fake_discount_detector.audit_discount(db, product)
        discount_trust = discount_audit.trust_score

        # 3. Seller Trust Signal (0-100)
        platform_name = product.current_best_platform or "amazon"
        mp_trust = marketplace_trust_engine.get_marketplace_trust(db, platform_name)
        seller_trust = mp_trust.trust_score

        # 4. Volatility Signal (0-100, lower volatility = higher score)
        vol = volatility_engine.calculate_volatility(db, product)
        volatility_signal = max(20.0, 100.0 - vol.volatility_score)

        # 5. Product Rating Signal (0-100)
        rating_signal = ((product.average_rating or 4.0) / 5.0) * 100.0

        # Weighted combination
        confidence = (
            price_quality * weights.price_quality
            + discount_trust * weights.historical_discount
            + seller_trust * weights.seller_trust
            + volatility_signal * weights.volatility
            + rating_signal * weights.user_affinity
        )

        return round(min(100.0, max(0.0, confidence)), 1)


# Singleton
buy_confidence_engine = BuyConfidenceScoreEngine()
