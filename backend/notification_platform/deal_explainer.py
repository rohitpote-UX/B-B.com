"""
Brand Battle — 15. AI Deal Explanation Engine
Provides contextual transparency for every alert ("Lowest verified price in the last 8 months from a highly trusted seller").
"""

from typing import Dict, Any


class AIDealExplanationEngine:
    """Generates transparent narrative explanations for deal alerts."""

    def explain_deal(
        self, product_name: str, historical_low: float, seller_trust: float
    ) -> str:
        """Format contextual deal explanation."""
        return (
            f"This isn't just a discount. It's the lowest verified price (₹{historical_low:,.0f}) "
            f"in the last eight months from a highly trusted seller ({seller_trust:.0f}/100 trust score)."
        )


# Singleton
ai_deal_explainer = AIDealExplanationEngine()
