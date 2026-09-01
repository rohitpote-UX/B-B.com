"""
Brand Battle — Behavioral Analysis & Session Graph Engine
Tracks anonymous browsing sessions, view sequences, and product co-occurrence patterns.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from models import Product
from logging_config import logger


class BehaviorEngine:
    """Tracks anonymous session browsing behavior and co-view patterns."""

    def __init__(self):
        # In-memory co-occurrence matrix fallback (product_id -> Dict[co_occurring_id, count])
        self._co_occurrence_graph = defaultdict(lambda: defaultdict(int))

    def record_session_view(self, session_id: str, product_id: int, history_sequence: Optional[List[int]] = None):
        """Record view event and update co-occurrence sequence graph."""
        if not history_sequence:
            return

        for prev_id in history_sequence:
            if prev_id != product_id:
                self._co_occurrence_graph[prev_id][product_id] += 1
                self._co_occurrence_graph[product_id][prev_id] += 1

    def get_people_also_viewed(
        self, 
        db: Session, 
        product_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate 'People Also Viewed' recommendations based on co-occurrence graph & search history."""
        try:
            co_occurring = self._co_occurrence_graph.get(product_id, {})
            sorted_co = sorted(co_occurring.items(), key=lambda x: x[1], reverse=True)[:limit]

            results = []
            for target_id, count in sorted_co:
                p = db.query(Product).filter(Product.id == target_id, Product.is_active == True).first()
                if p:
                    results.append({
                        "product": p,
                        "confidence": min(1.0, count / 10.0),
                        "reason": f"Frequently viewed together in recent browsing sessions ({count} co-views)"
                    })

            # Fallback if session history is empty: return products in same category with highest view count
            if len(results) < limit:
                target_p = db.query(Product).filter(Product.id == product_id).first()
                if target_p:
                    fallback_products = db.query(Product).filter(
                        Product.category_id == target_p.category_id,
                        Product.id != product_id,
                        Product.is_active == True
                    ).order_by(Product.view_count.desc()).limit(limit - len(results)).all()

                    for fp in fallback_products:
                        results.append({
                            "product": fp,
                            "confidence": 0.65,
                            "reason": "Popular choice among shoppers browsing this category"
                        })

            return results[:limit]
        except Exception as e:
            logger.error(f"Error computing behavioral recommendations for product {product_id}: {e}")
            return []
