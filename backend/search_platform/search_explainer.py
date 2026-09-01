"""
Brand Battle — Search Explainability Layer
Generates human-readable explanations for search result rankings.
"""

import logging
from typing import List, Dict, Any, Optional

from models import Product

logger = logging.getLogger("brandbattle.search.explainer")


class SearchExplainer:
    """Generates explainability data for search results."""

    def explain_result(
        self,
        product: Product,
        signal_breakdown: Dict[str, float],
        composite_score: float,
        query_brand: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a human-readable explanation for a single search result."""
        explanations: List[str] = []
        badges: List[str] = []

        # Keyword relevance
        kw = signal_breakdown.get("keyword_relevance", 0.0)
        if kw > 0.7:
            explanations.append("Exact keyword match")
            badges.append("Best Match")
        elif kw > 0.4:
            explanations.append(f"{int(kw * 100)}% keyword relevance")

        # Semantic similarity
        sem = signal_breakdown.get("semantic_similarity", 0.0)
        if sem > 0.6:
            explanations.append(f"{int(sem * 100)}% semantic similarity")
        elif sem > 0.3:
            explanations.append("Semantically related")

        # Brand match
        br = signal_breakdown.get("brand_reliability", 0.0)
        if query_brand and product.brand:
            if product.brand.name and product.brand.name.lower() == query_brand.lower():
                explanations.append("Exact brand match")
                badges.append("Brand Match")
            elif br > 0.7:
                explanations.append("Trusted brand")

        # Price competitiveness
        price = signal_breakdown.get("price_competitiveness", 0.0)
        if price > 0.7:
            explanations.append("Great deal available")
            badges.append("Great Deal")
        elif price > 0.4:
            explanations.append("Competitively priced")

        # Popularity
        pop = signal_breakdown.get("popularity", 0.0)
        if pop > 0.7:
            explanations.append("Highly popular")
            badges.append("Popular")
        elif pop > 0.4:
            explanations.append("Well-known product")

        # Trending
        trend = signal_breakdown.get("trending", 0.0)
        if trend > 0.5:
            explanations.append("Trending this week")
            badges.append("Trending")

        # Review quality
        review = signal_breakdown.get("review_quality", 0.0)
        if review > 0.7:
            rating = product.average_rating or 0.0
            count = product.total_reviews or 0
            explanations.append(f"Rated {rating:.1f}/5 ({count} reviews)")
            if rating >= 4.5:
                badges.append("Top Rated")

        # KG confidence
        kg = signal_breakdown.get("kg_confidence", 0.0)
        if kg > 0.3:
            explanations.append("Knowledge Graph verified")

        # Attribute match
        attr = signal_breakdown.get("attribute_match", 0.0)
        if attr > 0.3:
            explanations.append("Matches your specifications")

        # Availability
        avail = signal_breakdown.get("availability", 0.0)
        if avail >= 1.0:
            marketplace_count = 0
            if product.current_best_platform:
                marketplace_count = 1  # At least one
            if marketplace_count > 0:
                explanations.append(f"Available now")

        # Completeness
        comp = signal_breakdown.get("product_completeness", 0.0)
        if comp > 0.85:
            explanations.append("Complete product information")

        # Relevance percentage
        relevance_pct = int(composite_score * 100)

        return {
            "relevance_score": round(composite_score, 4),
            "relevance_percentage": min(99, max(1, relevance_pct)),
            "explanations": explanations[:6],  # Top 6 explanations
            "badges": badges[:3],  # Top 3 badges
            "signal_breakdown": signal_breakdown,
            "primary_reason": explanations[0] if explanations else "Relevant result",
        }


# Singleton
search_explainer = SearchExplainer()
