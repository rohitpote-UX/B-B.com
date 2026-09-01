"""
Brand Battle — AI Re-Ranking Engine
Post-ranking re-ordering based on intent, diversity, price-value, and behavioral trends.
Does not change retrieval — only improves ordering of the final ranked list.
"""

import logging
from typing import List, Dict, Any, Optional
from collections import Counter

from search_platform.config import search_config
from search_platform.intent_detector import ShoppingIntent

logger = logging.getLogger("brandbattle.search.reranking")


class RerankingEngine:
    """AI post-ranking re-ordering engine for result quality improvement."""

    def rerank(
        self,
        ranked_results: List[Dict[str, Any]],
        intent: Optional[ShoppingIntent] = None,
    ) -> List[Dict[str, Any]]:
        """
        Apply AI re-ranking to improve result ordering.
        Modifies composite_score in-place and re-sorts.
        """
        if not search_config.enable_reranking or not ranked_results:
            return ranked_results

        cfg = search_config.reranking

        # 1. Intent-aware boosting
        if intent:
            self._apply_intent_boost(ranked_results, intent, cfg)

        # 2. Diversity injection (penalize same-brand clustering)
        self._apply_diversity_penalty(ranked_results, cfg)

        # 3. Price-value ratio boosting
        self._apply_price_value_boost(ranked_results, cfg)

        # 4. Quality / completeness boosting
        self._apply_quality_boost(ranked_results, cfg)

        # Re-sort by updated composite score
        ranked_results.sort(key=lambda x: x.get("reranked_score", x.get("composite_score", 0)), reverse=True)

        return ranked_results

    def _apply_intent_boost(
        self, results: List[Dict[str, Any]],
        intent: ShoppingIntent, cfg: Any
    ) -> None:
        """Boost results aligned with detected shopping intent."""
        for item in results:
            product = item.get("product")
            if not product:
                continue

            base = item.get("composite_score", 0.0)
            boost = 1.0

            if intent.intent_type == ShoppingIntent.DEAL_HUNTING:
                # Boost products with high deal scores
                deal_score = getattr(product, "deal_score", None) or 0.0
                if deal_score > 70:
                    boost = cfg.intent_boost_factor
                elif deal_score > 40:
                    boost = 1.0 + (cfg.intent_boost_factor - 1.0) * 0.5

            elif intent.intent_type == ShoppingIntent.SPECIFIC_PRODUCT:
                # Boost exact keyword matches
                kw_score = item.get("keyword_score", 0.0)
                if kw_score > 0.7:
                    boost = cfg.intent_boost_factor

            elif intent.intent_type == ShoppingIntent.RESEARCHING:
                # Boost well-reviewed products
                rating = getattr(product, "average_rating", 0.0) or 0.0
                reviews = getattr(product, "total_reviews", 0) or 0
                if rating >= 4.0 and reviews >= 10:
                    boost = 1.0 + (cfg.intent_boost_factor - 1.0) * 0.7

            elif intent.intent_type == ShoppingIntent.COMPARING:
                # No specific boost for comparison — diversity matters more
                pass

            item["reranked_score"] = base * boost

    def _apply_diversity_penalty(
        self, results: List[Dict[str, Any]], cfg: Any
    ) -> None:
        """Penalize results from the same brand appearing in top positions."""
        brand_counts: Counter = Counter()

        for i, item in enumerate(results):
            product = item.get("product")
            if not product:
                continue

            brand_name = ""
            if product.brand:
                brand_name = product.brand.name or ""

            if i < 5 and brand_name:  # Only enforce diversity in top-5
                brand_counts[brand_name] += 1
                if brand_counts[brand_name] > cfg.max_same_brand_top5:
                    current = item.get("reranked_score", item.get("composite_score", 0.0))
                    item["reranked_score"] = current * cfg.diversity_penalty

    def _apply_price_value_boost(
        self, results: List[Dict[str, Any]], cfg: Any
    ) -> None:
        """Boost products with good price-value ratio."""
        for item in results:
            product = item.get("product")
            if not product:
                continue

            price = getattr(product, "current_best_price", None)
            rating = getattr(product, "average_rating", None) or 0.0

            if price and price > 0 and rating >= 4.0:
                # Good rating at any price = slight boost
                current = item.get("reranked_score", item.get("composite_score", 0.0))
                item["reranked_score"] = current * (1.0 + (cfg.price_value_boost - 1.0) * 0.5)

    def _apply_quality_boost(
        self, results: List[Dict[str, Any]], cfg: Any
    ) -> None:
        """Boost products with high data completeness."""
        for item in results:
            signals = item.get("signal_breakdown", {})
            completeness = signals.get("product_completeness", 0.0)

            if completeness > 0.85:
                current = item.get("reranked_score", item.get("composite_score", 0.0))
                item["reranked_score"] = current * cfg.quality_completeness_boost


# Singleton
reranking_engine = RerankingEngine()
