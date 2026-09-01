"""
Brand Battle — Trending & Momentum Engine
Identifies real-time trending products based on view velocity, search interest, wishlist momentum, and offer updates.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import Product, Deal
from logging_config import logger


class TrendingEngine:
    """Calculates product momentum and trending scores across active items."""

    def compute_trending_score(self, product: Product) -> float:
        """Calculate momentum velocity score."""
        views = getattr(product, 'view_count', 0) or 0
        compares = getattr(product, 'compare_count', 0) or 0
        deal_score = getattr(product, 'deal_score', 50.0) or 50.0
        rating = getattr(product, 'average_rating', 4.0) or 4.0

        # Weighted momentum velocity
        score = (views * 0.4) + (compares * 0.8) + (deal_score * 0.3) + (rating * 5.0)
        return round(score, 2)

    def get_trending_products(
        self, 
        db: Session, 
        category_id: Optional[int] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch real-time trending products with high momentum."""
        try:
            query = db.query(Product).filter(Product.is_active == True)
            if category_id:
                query = query.filter(Product.category_id == category_id)

            candidates = query.order_by(Product.view_count.desc(), Product.deal_score.desc()).limit(30).all()

            results = []
            for p in candidates:
                t_score = self.compute_trending_score(p)
                results.append({
                    "product": p,
                    "trending_score": t_score,
                    "confidence": min(1.0, t_score / 100.0),
                    "reason": f"High Demand Momentum (Trending Score: {t_score})"
                })

            results.sort(key=lambda x: x["trending_score"], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Error computing trending recommendations: {e}")
            return []
