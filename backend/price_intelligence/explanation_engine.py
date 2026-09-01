"""
Brand Battle — 16. Explainable AI Layer Engine
Generates transparent, human-readable explanations with zero black-box outputs.
"""

from typing import Dict, Any
from price_intelligence.schemas import (
    BuyRecommendationSchema, FairMarketValueSchema, FakeDiscountSchema, MarketplaceTrustSchema
)


class ExplainableAILayerEngine:
    """Translates complex scoring matrices into clear natural language explanations."""

    def generate_explanation(
        self,
        product_name: str,
        buy_rec: BuyRecommendationSchema,
        fair_value: FairMarketValueSchema,
        discount_audit: FakeDiscountSchema,
        trust: MarketplaceTrustSchema,
    ) -> str:
        """Synthesize human-readable decision narrative."""
        parts = [
            f"Buying decision '{buy_rec.decision}' for {product_name} (Confidence: {int(buy_rec.confidence_score * 100)}%).",
        ]

        if fair_value.underpriced_percentage > 0:
            parts.append(
                f"Current price is {fair_value.underpriced_percentage}% below calculated Fair Market Value of {fair_value.fair_price}."
            )
        elif fair_value.overpriced_percentage > 0:
            parts.append(
                f"Current price is {fair_value.overpriced_percentage}% above Fair Market Value of {fair_value.fair_price}."
            )

        if discount_audit.is_manipulated:
            parts.append(
                f"Warning: Claimed discount of {discount_audit.claimed_discount_pct}% contains ~{discount_audit.fake_discount_pct}% MRP inflation relative to historical averages."
            )
        else:
            parts.append(f"Discount integrity score is high ({discount_audit.trust_score}%).")

        parts.append(
            f"Marketplace trust rating for {trust.marketplace.title()} is {trust.trust_score}/100."
        )

        return " ".join(parts)


# Singleton
explanation_engine = ExplainableAILayerEngine()
