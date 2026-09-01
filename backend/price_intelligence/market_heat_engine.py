"""
Brand Battle — 17. Live Market Heat Engine
Generates real-time heat status (🔥 Selling Fast, 📈 Price Rising, 📉 Price Falling, 🟢 Best Time to Buy, 🔴 Expensive).
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.volatility_engine import volatility_engine


class LiveMarketHeatEngine:
    """Computes real-time market heat status indicators."""

    def determine_market_heat(self, db: Session, product: Product) -> str:
        """Calculate market heat status for a product."""
        fv = fair_value_engine.calculate_fair_value(db, product)
        vol = volatility_engine.calculate_volatility(db, product)

        views = product.view_count or 0
        if views > 500:
            return "🔥 Selling Fast"

        if fv.underpriced_percentage > 8.0:
            return "🟢 Best Time to Buy"
        elif fv.underpriced_percentage > 0:
            return "📉 Price Falling"
        elif fv.overpriced_percentage > 15.0:
            return "🔴 Expensive"
        elif fv.overpriced_percentage > 0:
            return "📈 Price Rising"
        else:
            return "🟠 Average Deal"


# Singleton
market_heat_engine = LiveMarketHeatEngine()
