"""
Brand Battle — 2. AI Buy Recommendation Engine
Produces explicit buying decisions: BUY NOW, WAIT, EXCELLENT DEAL, GOOD DEAL, OVERPRICED, NOT RECOMMENDED.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.buy_confidence import buy_confidence_engine
from price_intelligence.price_forecasting import price_forecasting_engine
from price_intelligence.schemas import BuyRecommendationSchema


class AIBuyAdvisorEngine:
    """Generates transparent AI buying decisions, reasoning, and predicted waiting period."""

    def advise_buy(self, db: Session, product: Product) -> BuyRecommendationSchema:
        """Calculate AI Buy Recommendation."""
        fv = fair_value_engine.calculate_fair_value(db, product)
        confidence = buy_confidence_engine.calculate_confidence(db, product) / 100.0
        forecast = price_forecasting_engine.forecast_prices(db, product)

        current = product.current_best_price or 0.0

        if fv.underpriced_percentage > 12.0:
            decision = "EXCELLENT DEAL"
            reason = f"Current price is {fv.underpriced_percentage}% below calculated Fair Market Value."
            prob_drop = 0.10
            wait_days = 0
            savings = fv.price_difference
        elif fv.underpriced_percentage > 3.0:
            decision = "BUY NOW"
            reason = "Current price is well aligned with historic low benchmarks."
            prob_drop = 0.20
            wait_days = 0
            savings = abs(fv.price_difference)
        elif fv.overpriced_percentage > 15.0:
            decision = "OVERPRICED"
            reason = f"Price is {fv.overpriced_percentage}% above Fair Market Value. High probability of price drop."
            prob_drop = 0.85
            wait_days = 21
            savings = round(current - forecast.d30_predicted_price, 2)
        elif fv.overpriced_percentage > 5.0:
            decision = "WAIT"
            reason = "Price is moderately elevated. Predicted to drop within 30 days."
            prob_drop = 0.65
            wait_days = 14
            savings = round(current - forecast.d7_predicted_price, 2)
        else:
            decision = "GOOD DEAL"
            reason = "Price is fair and within standard market range."
            prob_drop = 0.35
            wait_days = 7
            savings = 0.0

        return BuyRecommendationSchema(
            decision=decision,
            confidence_score=round(confidence, 2),
            reasoning=reason,
            predicted_savings=max(0.0, abs(savings)),
            expected_waiting_period_days=wait_days,
            probability_of_future_drop=prob_drop,
        )


# Singleton
ai_buy_advisor = AIBuyAdvisorEngine()
