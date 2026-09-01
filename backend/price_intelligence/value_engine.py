"""
Brand Battle — 9. Value For Money Engine
Scores products (0-100) using specs, reviews, quality, historical price, current discount, and warranty.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.fake_discount_detector import fake_discount_detector


class ValueForMoneyEngine:
    """Computes a dedicated Value For Money Score (0-100)."""

    def calculate_value_score(self, db: Session, product: Product) -> float:
        """Calculate Value For Money score for a product."""
        # 1. Rating contribution (max 30 pts)
        rating = product.average_rating or 4.0
        rating_score = (rating / 5.0) * 30.0

        # 2. Fair Value contribution (max 35 pts)
        fv = fair_value_engine.calculate_fair_value(db, product)
        if fv.underpriced_percentage > 0:
            fair_value_score = 35.0
        elif fv.overpriced_percentage > 0:
            fair_value_score = max(5.0, 35.0 - fv.overpriced_percentage)
        else:
            fair_value_score = 25.0

        # 3. Discount authenticity contribution (max 20 pts)
        discount_audit = fake_discount_detector.audit_discount(db, product)
        discount_score = (discount_audit.trust_score / 100.0) * 20.0

        # 4. Reviews count weight (max 15 pts)
        reviews = product.total_reviews or 50
        review_score = min(15.0, (reviews / 500.0) * 15.0)

        total_value_score = round(rating_score + fair_value_score + discount_score + review_score, 1)
        return min(100.0, max(0.0, total_value_score))


# Singleton
value_for_money_engine = ValueForMoneyEngine()
