"""
Brand Battle — 8. Price Volatility Engine
Measures variance, standard deviation, change frequency, and classifies volatility (Stable, Moderately Volatile, Highly Volatile).
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.price_history import price_history_engine
from price_intelligence.repository import price_intel_repo
from price_intelligence.utils import stddev, variance, mean
from price_intelligence.schemas import VolatilitySchema
from price_intelligence.config import price_intel_config


class PriceVolatilityEngine:
    """Calculates statistical price volatility and stability classifications."""

    def calculate_volatility(self, db: Session, product: Product) -> VolatilitySchema:
        """Compute variance, stddev, coefficient of variation, and volatility class."""
        snapshots = price_intel_repo.get_price_history_snapshots(db, product.id, days=90)
        prices = [s.effective_final_price for s in snapshots]

        if len(prices) < 2:
            return VolatilitySchema(
                variance=0.0,
                standard_deviation=0.0,
                volatility_score=10.0,
                classification="Stable",
                change_frequency="Low",
            )

        avg = mean(prices)
        stdev = stddev(prices)
        var = variance(prices)

        # Coefficient of variation (CV)
        cv = (stdev / avg) if avg > 0 else 0.0
        volatility_score = round(min(100.0, cv * 200.0), 2)

        if cv > price_intel_config.high_volatility_threshold:
            classification = "Highly Volatile"
            frequency = "High"
        elif cv > 0.10:
            classification = "Moderately Volatile"
            frequency = "Medium"
        else:
            classification = "Stable"
            frequency = "Low"

        return VolatilitySchema(
            variance=round(var, 2),
            standard_deviation=round(stdev, 2),
            volatility_score=volatility_score,
            classification=classification,
            change_frequency=frequency,
        )


# Singleton
volatility_engine = PriceVolatilityEngine()
