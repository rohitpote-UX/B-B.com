"""
Brand Battle — Product Popularity Scoring Engine
Computes normalized popularity signals from view counts, compare counts, reviews, and SearchMetadata.
"""

import math
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product, SearchMetadata

logger = logging.getLogger("brandbattle.search.popularity")


class PopularityEngine:
    """Computes normalized popularity scores for ranking."""

    def score_product(self, product: Product, db: Optional[Session] = None) -> Dict[str, float]:
        """Compute popularity signals for a single product."""
        views = product.view_count or 0
        compares = product.compare_count or 0
        reviews = product.total_reviews or 0

        # Logarithmic normalization for views (prevents high-view products from dominating)
        view_score = min(1.0, math.log10(views + 1) / 4.0) if views > 0 else 0.0

        # Compare engagement score
        compare_score = min(1.0, math.log10(compares + 1) / 3.0) if compares > 0 else 0.0

        # Review volume score
        review_score = min(1.0, math.log10(reviews + 1) / 2.5) if reviews > 0 else 0.0

        # Combined weighted popularity
        combined = (
            view_score * 0.50
            + compare_score * 0.25
            + review_score * 0.25
        )

        # Check SearchMetadata for pre-computed scores
        metadata_boost = 0.0
        if db and product.master_product_id:
            try:
                meta = (
                    db.query(SearchMetadata)
                    .filter(SearchMetadata.master_product_id == product.master_product_id)
                    .first()
                )
                if meta:
                    metadata_boost = (
                        (meta.popularity_score or 0.0) * 0.4
                        + (meta.click_score or 0.0) * 0.3
                        + (meta.comparison_score or 0.0) * 0.3
                    )
            except Exception:
                pass

        final = min(1.0, combined * 0.7 + metadata_boost * 0.3)

        return {
            "popularity_score": round(final, 4),
            "view_score": round(view_score, 4),
            "compare_score": round(compare_score, 4),
            "review_score": round(review_score, 4),
            "metadata_boost": round(metadata_boost, 4),
        }


# Singleton
popularity_engine = PopularityEngine()
