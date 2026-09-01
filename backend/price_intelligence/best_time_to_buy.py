"""
Brand Battle — 13. Best Time To Buy Engine
Identifies optimal buying window, best month, week, festival, and historical buying window.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.festival_engine import festival_engine
from price_intelligence.fair_value_engine import fair_value_engine


class BestTimeToBuyEngine:
    """Identifies historical and predicted optimal buying windows."""

    def evaluate_best_time(self, db: Session, product: Product) -> Dict[str, Any]:
        """Compute optimal time to buy insights."""
        fv = fair_value_engine.calculate_fair_value(db, product)
        upcoming_fest = festival_engine.get_upcoming_festival()

        if fv.underpriced_percentage > 5.0:
            optimal_window = "Buy Now — Current Price Below Fair Value"
            expected_savings = fv.price_difference
        else:
            optimal_window = f"Wait for {upcoming_fest['festival_name']}"
            expected_savings = round((product.current_best_price or 0.0) * (upcoming_fest['expected_drop_pct'] / 100.0), 2)

        return {
            "optimal_window": optimal_window,
            "best_month": upcoming_fest["target_month"],
            "best_festival": upcoming_fest["festival_name"],
            "expected_savings": abs(expected_savings),
            "historical_best_period": "Q4 Holiday Season & Great Indian Festival",
        }


# Singleton
best_time_to_buy_engine = BestTimeToBuyEngine()
