"""
Brand Battle — Search Query Classifier
Classifies parsed queries into primary + secondary search intent types.
"""

import logging
from typing import Dict, Any, List, Tuple
from search_platform.query_parser import ParsedQuery

logger = logging.getLogger("brandbattle.search.classifier")


class QueryClassification:
    """Classification result with primary and secondary intent types."""

    BRAND_SEARCH = "brand_search"
    CATEGORY_SEARCH = "category_search"
    PRODUCT_SEARCH = "product_search"
    COMPARISON_SEARCH = "comparison_search"
    QUESTION_SEARCH = "question_search"
    PRICE_SEARCH = "price_search"
    ACCESSORY_SEARCH = "accessory_search"
    REVIEW_SEARCH = "review_search"
    DEAL_SEARCH = "deal_search"
    RECOMMENDATION_SEARCH = "recommendation_search"
    MIXED_INTENT = "mixed_intent"

    def __init__(self, primary: str, secondary: List[str] = None, confidence: float = 0.9):
        self.primary = primary
        self.secondary = secondary or []
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "confidence": self.confidence,
        }


# Keywords that strongly signal specific search types
_ACCESSORY_KEYWORDS = {"case", "cover", "charger", "cable", "adapter", "stand", "mount", "screen protector", "strap", "band"}
_REVIEW_KEYWORDS = {"review", "reviews", "opinion", "opinions", "feedback", "rating", "ratings"}
_RECOMMENDATION_KEYWORDS = {"best", "top", "recommend", "recommended", "suggestion", "suggest", "popular", "trending", "good"}


class QueryClassifier:
    """Classifies parsed queries into primary and secondary intent types."""

    def classify(self, parsed: ParsedQuery) -> QueryClassification:
        """Classify a parsed query into intent categories."""
        if not parsed.raw_query.strip():
            return QueryClassification(QueryClassification.CATEGORY_SEARCH, confidence=0.5)

        signals: List[Tuple[str, float]] = []
        tokens_set = set(parsed.tokens)

        # 1. Comparison search
        if parsed.is_comparison:
            signals.append((QueryClassification.COMPARISON_SEARCH, 0.95))

        # 2. Deal search
        if parsed.is_deal_search:
            signals.append((QueryClassification.DEAL_SEARCH, 0.90))

        # 3. Review search
        if tokens_set & _REVIEW_KEYWORDS:
            signals.append((QueryClassification.REVIEW_SEARCH, 0.88))

        # 4. Accessory search
        if tokens_set & _ACCESSORY_KEYWORDS:
            signals.append((QueryClassification.ACCESSORY_SEARCH, 0.85))

        # 5. Price search (dominant price constraint, no other strong signals)
        if (parsed.price_min is not None or parsed.price_max is not None) and not parsed.brand and not parsed.product_type:
            signals.append((QueryClassification.PRICE_SEARCH, 0.80))

        # 6. Recommendation search (superlatives + question intent)
        if parsed.has_superlative and (parsed.is_question or not parsed.brand):
            signals.append((QueryClassification.RECOMMENDATION_SEARCH, 0.85))

        # 7. Question search
        if parsed.is_question and not parsed.has_superlative:
            signals.append((QueryClassification.QUESTION_SEARCH, 0.75))

        # 8. Brand search (brand detected, no specific product type)
        if parsed.brand and not parsed.product_type and not parsed.category:
            signals.append((QueryClassification.BRAND_SEARCH, 0.82))

        # 9. Category search (category detected, no brand)
        if parsed.category and not parsed.brand:
            signals.append((QueryClassification.CATEGORY_SEARCH, 0.80))

        # 10. Product search (specific product terms or brand + type)
        if parsed.brand and parsed.product_type:
            signals.append((QueryClassification.PRODUCT_SEARCH, 0.90))
        elif len(parsed.remaining_keywords) >= 2 and parsed.brand:
            signals.append((QueryClassification.PRODUCT_SEARCH, 0.78))

        # Sort by confidence descending
        signals.sort(key=lambda x: x[1], reverse=True)

        if not signals:
            # Fallback: if we have remaining keywords, treat as mixed intent
            if parsed.remaining_keywords:
                return QueryClassification(QueryClassification.MIXED_INTENT, confidence=0.6)
            return QueryClassification(QueryClassification.CATEGORY_SEARCH, confidence=0.5)

        primary = signals[0][0]
        primary_conf = signals[0][1]
        secondary = [s[0] for s in signals[1:] if s[0] != primary]

        # If multiple strong signals (>= 2 with confidence > 0.7), mark as mixed
        strong_signals = [s for s in signals if s[1] > 0.7]
        if len(strong_signals) >= 3:
            primary = QueryClassification.MIXED_INTENT
            primary_conf = 0.85
            secondary = [s[0] for s in signals if s[0] != QueryClassification.MIXED_INTENT]

        return QueryClassification(
            primary=primary,
            secondary=secondary[:3],
            confidence=round(primary_conf, 2)
        )


# Singleton
query_classifier = QueryClassifier()
