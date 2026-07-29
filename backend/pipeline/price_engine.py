"""
Brand Battle - Intelligent Price Engine
Tracks multi-platform pricing, logs timestamped price histories, and detects artificial/fake discounts.
"""

from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger("brandbattle.price_engine")


class PriceEngine:
    """Evaluates multi-marketplace prices, logs historical trends, and assesses discount authenticity."""

    @staticmethod
    def calculate_deal_metrics(price: float, original_price: Optional[float] = None) -> Tuple[float, float, bool]:
        """
        Calculates discount percentage, deal quality score (0-100), and fake discount flag.
        Returns: (discount_pct, deal_score, is_fake_discount)
        """
        if not original_price or original_price <= price:
            return 0.0, 50.0, False

        discount_pct = round(((original_price - price) / original_price) * 100.0, 1)

        # Flag suspicious discounts (> 70% discount on tech/electronics is often artificial MRP inflation)
        is_fake_discount = discount_pct > 70.0

        # Deal score formula: scales with discount percentage, penalized if fake
        deal_score = min(100.0, max(0.0, discount_pct * 1.5))
        if is_fake_discount:
            deal_score = max(20.0, deal_score * 0.4)

        return discount_pct, round(deal_score, 1), is_fake_discount

    def process_price_update(
        self, product_id: int, platform: str, price: float, original_price: Optional[float], url: str
    ) -> Dict[str, Any]:
        """Generates structured payload for updating Price and PriceHistory tables."""
        discount_pct, deal_score, is_fake = self.calculate_deal_metrics(price, original_price)

        return {
            "product_id": product_id,
            "platform": platform,
            "price": price,
            "original_price": original_price or price,
            "discount_percentage": discount_pct,
            "deal_score": deal_score,
            "is_fake_discount": is_fake,
            "url": url,
            "is_available": True,
            "updated_at": datetime.utcnow()
        }
