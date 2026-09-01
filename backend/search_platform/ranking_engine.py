"""
Brand Battle — Search Ranking Engine
Composite 16-signal ranking engine that produces explainable, weighted relevance scores.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.ranking")


class RankingEngine:
    """Multi-signal composite ranking engine with configurable weights."""

    def rank(
        self,
        candidates: List[Dict[str, Any]],
        parsed_query: Any = None,
        user_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rank a merged candidate list using 16 configurable scoring signals.
        Each candidate dict must contain a 'product' key with a Product ORM object.
        Returns the same list sorted by composite_score descending.
        """
        weights = search_config.weights

        scored = []
        for candidate in candidates:
            product = candidate.get("product")
            if not product:
                continue

            signals = {}

            # 1. Keyword relevance (from keyword_search)
            signals["keyword_relevance"] = candidate.get("keyword_score", 0.0)

            # 2. Semantic similarity (from semantic_search)
            signals["semantic_similarity"] = candidate.get("semantic_score", 0.0)

            # 3. KG confidence (from knowledge_graph_search)
            signals["kg_confidence"] = candidate.get("kg_score", 0.0)

            # 4. Brand reliability
            signals["brand_reliability"] = self._score_brand_reliability(product)

            # 5. Marketplace reliability
            signals["marketplace_reliability"] = candidate.get("marketplace_score", 0.0)

            # 6. Offer freshness
            signals["offer_freshness"] = candidate.get("freshness_score", self._score_freshness(product))

            # 7. Price competitiveness
            signals["price_competitiveness"] = self._score_price_competitiveness(product)

            # 8. Product completeness
            signals["product_completeness"] = self._score_completeness(product)

            # 9. Popularity
            signals["popularity"] = candidate.get("popularity_score", self._score_popularity(product))

            # 10. Trending
            signals["trending"] = candidate.get("trending_score", 0.0)

            # 11. Availability
            signals["availability"] = 1.0 if product.is_active else 0.0

            # 12. Review quality
            signals["review_quality"] = self._score_review_quality(product)

            # 13. Recommendation affinity
            signals["recommendation_affinity"] = candidate.get("recommendation_score", 0.0)

            # 14. User preference
            signals["user_preference"] = candidate.get("personalization_score", 0.0)

            # 15. Historical CTR
            signals["historical_ctr"] = candidate.get("ctr_score", 0.0)

            # 16. Attribute match
            signals["attribute_match"] = candidate.get("attribute_score", 0.0)

            # Compute weighted composite score
            composite = (
                signals["keyword_relevance"] * weights.keyword_relevance
                + signals["semantic_similarity"] * weights.semantic_similarity
                + signals["kg_confidence"] * weights.kg_confidence
                + signals["brand_reliability"] * weights.brand_reliability
                + signals["marketplace_reliability"] * weights.marketplace_reliability
                + signals["offer_freshness"] * weights.offer_freshness
                + signals["price_competitiveness"] * weights.price_competitiveness
                + signals["product_completeness"] * weights.product_completeness
                + signals["popularity"] * weights.popularity
                + signals["trending"] * weights.trending
                + signals["availability"] * weights.availability
                + signals["review_quality"] * weights.review_quality
                + signals["recommendation_affinity"] * weights.recommendation_affinity
                + signals["user_preference"] * weights.user_preference
                + signals["historical_ctr"] * weights.historical_ctr
                + signals["attribute_match"] * weights.attribute_match
            )

            candidate["composite_score"] = round(composite, 6)
            candidate["signal_breakdown"] = {k: round(v, 4) for k, v in signals.items()}

            scored.append(candidate)

        # Sort by composite score descending
        scored.sort(key=lambda x: x["composite_score"], reverse=True)

        return scored

    def _score_brand_reliability(self, product: Product) -> float:
        """Score brand trust/reliability (0-1)."""
        if product.brand:
            trust = getattr(product.brand, "trust_score", 0.0) or 0.0
            return min(1.0, trust / 10.0)  # trust_score is 0-10
        return 0.3  # Unknown brand baseline

    def _score_freshness(self, product: Product) -> float:
        """Score product data freshness (0-1)."""
        if product.updated_at:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            try:
                updated = product.updated_at
                if updated.tzinfo is None:
                    from datetime import timezone as tz
                    updated = updated.replace(tzinfo=tz.utc)
                age_days = (now - updated).days
                if age_days < 1:
                    return 1.0
                elif age_days < 7:
                    return 0.9
                elif age_days < 30:
                    return 0.7
                elif age_days < 90:
                    return 0.5
                else:
                    return 0.3
            except Exception:
                return 0.5
        return 0.5

    def _score_price_competitiveness(self, product: Product) -> float:
        """Score price competitiveness (0-1) based on deal_score."""
        deal_score = product.deal_score or 0.0
        return min(1.0, deal_score / 100.0)

    def _score_completeness(self, product: Product) -> float:
        """Score product data completeness (0-1)."""
        filled = 0
        total = 7
        if product.name:
            filled += 1
        if product.description:
            filled += 1
        if product.image_url:
            filled += 1
        if product.specifications:
            filled += 1
        if product.features:
            filled += 1
        if product.brand_id:
            filled += 1
        if product.category_id:
            filled += 1
        return filled / total

    def _score_popularity(self, product: Product) -> float:
        """Score product popularity (0-1) from view/compare counts."""
        views = product.view_count or 0
        compares = product.compare_count or 0
        raw = views * 0.7 + compares * 0.3
        # Logarithmic normalization
        import math
        if raw <= 0:
            return 0.0
        return min(1.0, math.log10(raw + 1) / 4.0)

    def _score_review_quality(self, product: Product) -> float:
        """Score review quality (0-1) from rating and review count."""
        rating = product.average_rating or 0.0
        reviews = product.total_reviews or 0

        rating_score = min(1.0, rating / 5.0)
        # Bayesian-style: weight by review count
        review_weight = min(1.0, reviews / 50.0)

        return rating_score * 0.7 + review_weight * 0.3


# Singleton
ranking_engine = RankingEngine()
