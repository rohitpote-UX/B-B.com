"""
Brand Battle — Value Scoring Engine
Calculates composite value-for-money index and generates editorial badges (Best Value, Editor's Choice, Smart Buy).
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import Product
from logging_config import logger


class ValueEngine:
    """Evaluates value proposition based on features, price positioning, ratings, and discounts."""

    def calculate_value_score(self, product: Product) -> float:
        """Calculate composite 0-100 value score."""
        if not product or not product.current_best_price:
            return 50.0

        # Component 1: Rating score (0-30)
        rating = product.average_rating or 4.0
        rating_score = (rating / 5.0) * 30.0

        # Component 2: Deal quality score (0-30)
        deal_score = product.deal_score or 70.0
        deal_component = (deal_score / 100.0) * 30.0

        # Component 3: Discount savings (0-20)
        discount_score = 0.0
        if product.highest_price and product.highest_price > product.current_best_price:
            discount_pct = (product.highest_price - product.current_best_price) / product.highest_price
            discount_score = min(discount_pct * 100.0, 20.0)
        else:
            discount_score = 10.0

        # Component 4: Review confidence volume (0-20)
        review_count = product.total_reviews or 0
        volume_score = min(20.0, (review_count / 500.0) * 20.0)

        total_value = rating_score + deal_component + discount_score + volume_score
        return round(min(100.0, max(0.0, total_value)), 2)

    def assign_value_label(self, score: float) -> str:
        """Assign editorial recommendation badge based on value score."""
        if score >= 90.0:
            return "Editor's Choice"
        elif score >= 80.0:
            return "Best Value"
        elif score >= 70.0:
            return "Smart Buy"
        else:
            return "Recommended"

    def get_best_value_products(
        self, 
        db: Session, 
        category_id: Optional[int] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch top products with highest value-for-money scores."""
        try:
            query = db.query(Product).filter(Product.is_active == True)
            if category_id:
                query = query.filter(Product.category_id == category_id)

            products = query.limit(50).all()
            
            scored_list = []
            for p in products:
                val_score = self.calculate_value_score(p)
                label = self.assign_value_label(val_score)
                scored_list.append({
                    "product": p,
                    "value_score": val_score,
                    "badge": label,
                    "reason": f"Rated {label} with a composite Value Score of {val_score}/100"
                })

            scored_list.sort(key=lambda x: x["value_score"], reverse=True)
            return scored_list[:limit]
        except Exception as e:
            logger.error(f"Error computing best value recommendations: {e}")
            return []
