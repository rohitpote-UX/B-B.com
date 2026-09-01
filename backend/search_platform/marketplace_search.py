"""
Brand Battle — Marketplace Offer-Level Search Engine
Queries MarketplaceOffer table for title/price matching and maps offers back to products.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from models import Product, MarketplaceOffer
from search_platform.query_parser import ParsedQuery

logger = logging.getLogger("brandbattle.search.marketplace")


class MarketplaceSearch:
    """Offer-level retrieval engine over MarketplaceOffer table."""

    def search(
        self,
        parsed: ParsedQuery,
        candidate_ids: List[int],
        db: Session,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """Search marketplace offers by title/price and map to products."""
        search_tokens = []
        if parsed.remaining_keywords:
            search_tokens.extend(parsed.remaining_keywords[:5])
        if parsed.brand:
            search_tokens.append(parsed.brand)
        if parsed.product_type:
            search_tokens.append(parsed.product_type)

        if not search_tokens:
            return []

        # Build ILIKE filters on offer titles
        title_filters = []
        for token in search_tokens:
            if len(token) >= 2:
                title_filters.append(MarketplaceOffer.title.ilike(f"%{token}%"))

        if not title_filters:
            return []

        q = db.query(MarketplaceOffer).filter(
            or_(*title_filters),
            MarketplaceOffer.is_available == True,
            MarketplaceOffer.status == "active",
        )

        # Price filtering at offer level
        if parsed.price_min is not None:
            q = q.filter(MarketplaceOffer.price >= parsed.price_min)
        if parsed.price_max is not None:
            q = q.filter(MarketplaceOffer.price <= parsed.price_max)

        offers = q.limit(limit * 2).all()

        # Map offers to unique master_product_ids, then to products
        master_id_scores: Dict[int, float] = {}
        for offer in offers:
            mid = offer.master_product_id
            # Score based on offer quality signals
            score = 0.0
            title_lower = (offer.title or "").lower()
            for token in search_tokens:
                if token.lower() in title_lower:
                    score += 0.2

            # Boost available, high-rated offers
            if offer.rating and offer.rating >= 4.0:
                score += 0.1
            if offer.freshness_score and offer.freshness_score > 0.7:
                score += 0.05

            master_id_scores[mid] = max(master_id_scores.get(mid, 0.0), score)

        if not master_id_scores:
            return []

        # Resolve to products
        master_ids = list(master_id_scores.keys())
        product_q = (
            db.query(Product)
            .filter(
                Product.master_product_id.in_(master_ids),
                Product.is_active == True,
            )
            .options(joinedload(Product.brand), joinedload(Product.category))
        )

        if candidate_ids:
            product_q = product_q.filter(Product.id.in_(candidate_ids))

        products = product_q.limit(limit).all()

        results = []
        for product in products:
            score = master_id_scores.get(product.master_product_id, 0.0)
            results.append({
                "product": product,
                "marketplace_score": round(min(1.0, score), 4),
                "source": "marketplace_search",
            })

        results.sort(key=lambda x: x["marketplace_score"], reverse=True)
        return results[:limit]


# Singleton
marketplace_search = MarketplaceSearch()
