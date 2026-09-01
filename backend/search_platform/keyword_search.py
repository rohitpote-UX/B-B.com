"""
Brand Battle — BM25-Style Keyword Search Engine
Lexical token matching over Product fields with term frequency scoring.
"""

import re
import logging
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from models import Product
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.keyword")


class KeywordSearch:
    """BM25-inspired lexical keyword search engine over product text fields."""

    def search(
        self,
        tokens: List[str],
        candidate_ids: List[int],
        db: Session,
        limit: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        Search products by keyword token matching within the candidate pool.
        Returns scored results sorted by keyword relevance.
        """
        if not tokens:
            return []

        # Build ILIKE filters for each token
        filters = []
        for token in tokens[:8]:  # Limit tokens to prevent query explosion
            if len(token) < 2:
                continue
            pattern = f"%{token}%"
            filters.append(Product.name.ilike(pattern))
            filters.append(Product.description.ilike(pattern))
            filters.append(Product.short_description.ilike(pattern))

        if not filters:
            return []

        q = db.query(Product).filter(
            Product.is_active == True,
            or_(*filters)
        )

        # Scope to candidate pool if provided
        if candidate_ids:
            q = q.filter(Product.id.in_(candidate_ids))

        products = (
            q.options(joinedload(Product.brand), joinedload(Product.category))
            .limit(limit)
            .all()
        )

        # Score each product based on token matches
        results = []
        for product in products:
            score = self._compute_relevance_score(product, tokens)
            results.append({
                "product": product,
                "keyword_score": score,
                "source": "keyword_search",
            })

        # Sort by score descending
        results.sort(key=lambda x: x["keyword_score"], reverse=True)

        return results[:limit]

    def _compute_relevance_score(self, product: Product, tokens: List[str]) -> float:
        """Compute BM25-inspired relevance score based on field-weighted token matching."""
        score = 0.0
        name_lower = (product.name or "").lower()
        desc_lower = (product.description or "").lower()
        short_desc_lower = (product.short_description or "").lower()
        tags_str = " ".join(product.tags or []).lower() if product.tags else ""
        features_str = " ".join(product.features or []).lower() if product.features else ""

        for token in tokens:
            t = token.lower()
            if len(t) < 2:
                continue

            # Field-weighted scoring (name > short_desc > tags > features > description)
            if t in name_lower:
                # Exact word boundary match gets higher score
                if re.search(r'\b' + re.escape(t) + r'\b', name_lower):
                    score += 3.0
                else:
                    score += 2.0

            if t in short_desc_lower:
                score += 1.2

            if t in tags_str:
                score += 1.0

            if t in features_str:
                score += 0.8

            if t in desc_lower:
                score += 0.5

        # Normalize by number of tokens
        if tokens:
            score = score / len(tokens)

        return min(1.0, score / 3.0)  # Normalize to 0-1 range


# Singleton
keyword_search = KeywordSearch()
