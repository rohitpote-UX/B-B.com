"""
Brand Battle — 12. AI Negotiation Assistant Engine
Generates recommended negotiation counter-prices, seller acceptance probability, and strategic talking points.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.price_history import price_history_engine
from price_intelligence.schemas import NegotiationAssistantSchema


class AINegotiationAssistantEngine:
    """Calculates counter-offer pricing strategies and acceptance probability."""

    def calculate_negotiation_strategy(self, db: Session, product: Product) -> NegotiationAssistantSchema:
        """Compute recommended counter-offer and talking points."""
        current = product.current_best_price or product.lowest_price or 0.0
        fv = fair_value_engine.calculate_fair_value(db, product)
        timeline = price_history_engine.get_timeline_summary(db, product)

        lowest_90d = timeline.get("d90_lowest", current)

        # Counter-offer formula: 90-day lowest or fair market value
        counter_offer = round(min(fv.fair_price, lowest_90d), 2)
        if counter_offer >= current:
            counter_offer = round(current * 0.92, 2)

        # Acceptance probability
        price_diff_pct = ((current - counter_offer) / current) * 100
        if price_diff_pct <= 5.0:
            prob = 85.0
        elif price_diff_pct <= 12.0:
            prob = 65.0
        elif price_diff_pct <= 20.0:
            prob = 40.0
        else:
            prob = 20.0

        talking_points = [
            f"Current price is {round(price_diff_pct, 1)}% above the 90-day historical low of {lowest_90d}.",
            f"Statistically calculated Fair Market Value is {fv.fair_price}.",
            f"Competitor marketplace baselines indicate realistic transaction clearance at {counter_offer}.",
        ]

        return NegotiationAssistantSchema(
            current_price=current,
            recommended_counter_offer=counter_offer,
            fair_value=fv.fair_price,
            acceptance_probability_pct=prob,
            talking_points=talking_points,
        )


# Singleton
ai_negotiation_assistant = AINegotiationAssistantEngine()
