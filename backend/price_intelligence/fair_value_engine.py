"""
Brand Battle — 3. Fair Market Value Engine
Calculates statistically expected fair price based on historical trends, marketplace averages, category baselines, and specs.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.price_history import price_history_engine
from price_intelligence.schemas import FairMarketValueSchema


class FairValueEngine:
    """Calculates fair market price and overpriced/underpriced percentages."""

    def calculate_fair_value(self, db: Session, product: Product) -> FairMarketValueSchema:
        """Compute fair market value for a product."""
        current = product.current_best_price or product.lowest_price or 0.0
        timeline = price_history_engine.get_timeline_summary(db, product)

        avg_price = timeline.get("average_price", current)
        lowest_90d = timeline.get("d90_lowest", current)

        # Fair price model: weighted average of 90-day lowest and average price
        if avg_price > 0:
            fair_price = round(avg_price * 0.7 + lowest_90d * 0.3, 2)
        else:
            fair_price = current

        diff = round(current - fair_price, 2)

        if current > fair_price:
            overpriced_pct = round(((current - fair_price) / fair_price) * 100, 2)
            underpriced_pct = 0.0
            status = "Overpriced" if overpriced_pct > 10 else "Slightly Overpriced"
        elif current < fair_price:
            underpriced_pct = round(((fair_price - current) / fair_price) * 100, 2)
            overpriced_pct = 0.0
            status = "Underpriced" if underpriced_pct > 5 else "Fairly Priced"
        else:
            overpriced_pct = 0.0
            underpriced_pct = 0.0
            status = "Fairly Priced"

        return FairMarketValueSchema(
            current_price=current,
            fair_price=fair_price,
            price_difference=diff,
            overpriced_percentage=overpriced_pct,
            underpriced_percentage=underpriced_pct,
            status=status,
        )


# Singleton
fair_value_engine = FairValueEngine()
