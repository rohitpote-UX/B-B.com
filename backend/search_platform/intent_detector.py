"""
Brand Battle — Shopping Intent Detector
Combines parsed query and classification into a unified shopping intent signal.
"""

import logging
from typing import Dict, Any
from search_platform.query_parser import ParsedQuery
from search_platform.query_classifier import QueryClassification

logger = logging.getLogger("brandbattle.search.intent")


class ShoppingIntent:
    """Detected shopping intent with type and confidence."""

    SHOPPING = "shopping"
    RESEARCHING = "researching"
    COMPARING = "comparing"
    DEAL_HUNTING = "deal_hunting"
    BROWSING = "browsing"
    SPECIFIC_PRODUCT = "specific_product"

    def __init__(self, intent_type: str, confidence: float = 0.8, signals: Dict[str, Any] = None):
        self.intent_type = intent_type
        self.confidence = confidence
        self.signals = signals or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_type": self.intent_type,
            "confidence": self.confidence,
            "signals": self.signals,
        }


class IntentDetector:
    """Detects the user's shopping intent from parsed query and classification."""

    def detect(self, parsed: ParsedQuery, classification: QueryClassification) -> ShoppingIntent:
        """Analyze parsed query and classification to determine shopping intent."""
        signals = {}

        # 1. Comparison intent
        if parsed.is_comparison or classification.primary == QueryClassification.COMPARISON_SEARCH:
            return ShoppingIntent(
                ShoppingIntent.COMPARING, 0.92,
                {"trigger": "comparison_keywords_detected"}
            )

        # 2. Deal hunting intent
        if parsed.is_deal_search or classification.primary == QueryClassification.DEAL_SEARCH:
            return ShoppingIntent(
                ShoppingIntent.DEAL_HUNTING, 0.90,
                {"trigger": "deal_keywords_detected"}
            )

        # 3. Specific product search (brand + type or product name)
        if classification.primary == QueryClassification.PRODUCT_SEARCH:
            return ShoppingIntent(
                ShoppingIntent.SPECIFIC_PRODUCT, 0.88,
                {"trigger": "product_search_classified", "brand": parsed.brand}
            )

        # 4. Research / question intent
        if parsed.is_question or classification.primary in (
            QueryClassification.QUESTION_SEARCH,
            QueryClassification.REVIEW_SEARCH,
            QueryClassification.RECOMMENDATION_SEARCH
        ):
            return ShoppingIntent(
                ShoppingIntent.RESEARCHING, 0.82,
                {"trigger": "question_or_recommendation_intent"}
            )

        # 5. Active shopping intent (brand + price constraint)
        if parsed.brand and (parsed.price_min is not None or parsed.price_max is not None):
            return ShoppingIntent(
                ShoppingIntent.SHOPPING, 0.85,
                {"trigger": "brand_with_price_constraint", "brand": parsed.brand}
            )

        # 6. Shopping intent (has specific filters)
        if parsed.color or parsed.material or parsed.product_type:
            return ShoppingIntent(
                ShoppingIntent.SHOPPING, 0.78,
                {"trigger": "specific_filters_detected"}
            )

        # 7. Browsing intent (generic category or brand exploration)
        if classification.primary in (QueryClassification.BRAND_SEARCH, QueryClassification.CATEGORY_SEARCH):
            return ShoppingIntent(
                ShoppingIntent.BROWSING, 0.70,
                {"trigger": "brand_or_category_exploration"}
            )

        # 8. Default: general shopping
        return ShoppingIntent(
            ShoppingIntent.SHOPPING, 0.60,
            {"trigger": "default_shopping_intent"}
        )


# Singleton
intent_detector = IntentDetector()
