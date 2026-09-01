"""
Brand Battle — 4. Fake Discount Detection Engine
Identifies manipulated original MRP prices, calculating real discount % vs fake inflated discount %.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.price_history import price_history_engine
from price_intelligence.schemas import FakeDiscountSchema
from price_intelligence.config import price_intel_config


class FakeDiscountDetector:
    """Detects MRP manipulation and fake strike-through discount claims."""

    def audit_discount(self, db: Session, product: Product) -> FakeDiscountSchema:
        """Audit product claimed discount against historical Selling Price & MRP benchmarks."""
        current_price = product.current_best_price or product.lowest_price or 0.0
        claimed_mrp = getattr(product, 'highest_price', None) or getattr(product, 'original_price', None) or current_price * 1.25

        timeline = price_history_engine.get_timeline_summary(db, product)
        avg_historical_mrp = timeline.get("lifetime_highest", claimed_mrp)

        # Claimed discount percentage
        if claimed_mrp > current_price and claimed_mrp > 0:
            claimed_discount_pct = round(((claimed_mrp - current_price) / claimed_mrp) * 100, 2)
        else:
            claimed_discount_pct = 0.0

        # Real discount percentage (against historical average selling price)
        avg_selling_price = timeline.get("average_price", current_price)
        if avg_selling_price > current_price and avg_selling_price > 0:
            real_discount_pct = round(((avg_selling_price - current_price) / avg_selling_price) * 100, 2)
        else:
            real_discount_pct = 0.0

        # Fake discount percentage (claimed discount minus real discount)
        fake_discount_pct = max(0.0, round(claimed_discount_pct - real_discount_pct, 2))
        is_manipulated = fake_discount_pct > price_intel_config.fake_discount_threshold_pct

        # Trust score (0-100)
        trust_score = round(max(0.0, 100.0 - (fake_discount_pct * 2.0)), 2)

        return FakeDiscountSchema(
            claimed_mrp=round(claimed_mrp, 2),
            historical_avg_mrp=round(avg_historical_mrp, 2),
            current_price=round(current_price, 2),
            claimed_discount_pct=claimed_discount_pct,
            real_discount_pct=real_discount_pct,
            fake_discount_pct=fake_discount_pct,
            is_manipulated=is_manipulated,
            trust_score=trust_score,
        )


# Singleton
fake_discount_detector = FakeDiscountDetector()
