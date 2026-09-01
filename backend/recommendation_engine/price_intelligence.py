"""
Brand Battle — Price Intelligence Engine
Analyzes price tiers, identifies budget alternatives and premium upgrades, and evaluates price stability.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import Product
from recommendation_engine.recommendation_config import recommendation_settings
from logging_config import logger


class PriceIntelligence:
    """Evaluates price tiers and isolates budget vs. upgrade alternatives."""

    def get_budget_alternatives(
        self, 
        db: Session, 
        product: Product, 
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        """Identify lower-cost items in the same category offering comparable features."""
        if not product or not product.current_best_price:
            return []

        try:
            baseline_price = product.current_best_price
            max_budget_price = baseline_price * recommendation_settings.thresholds.budget_max_ratio

            candidates = db.query(Product).filter(
                Product.category_id == product.category_id,
                Product.id != product.id,
                Product.current_best_price <= max_budget_price,
                Product.is_active == True
            ).order_by(Product.deal_score.desc(), Product.average_rating.desc()).limit(limit).all()

            results = []
            for c in candidates:
                savings_pct = int(((baseline_price - c.current_best_price) / baseline_price) * 100)
                results.append({
                    "product": c,
                    "price_tier": "budget",
                    "confidence": 0.88,
                    "savings_percentage": savings_pct,
                    "reason": f"{savings_pct}% lower cost than baseline ({c.average_rating or 4.0}/5 buyer rating)"
                })
            return results
        except Exception as e:
            logger.error(f"Error computing budget alternatives for product {product.id}: {e}")
            return []

    def get_premium_upgrades(
        self, 
        db: Session, 
        product: Product, 
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        """Identify higher-end models offering superior hardware or performance."""
        if not product or not product.current_best_price:
            return []

        try:
            baseline_price = product.current_best_price
            min_upgrade_price = baseline_price * recommendation_settings.thresholds.upgrade_min_ratio
            max_upgrade_price = baseline_price * recommendation_settings.thresholds.upgrade_max_ratio

            candidates = db.query(Product).filter(
                Product.category_id == product.category_id,
                Product.id != product.id,
                Product.current_best_price >= min_upgrade_price,
                Product.current_best_price <= max_upgrade_price,
                Product.is_active == True
            ).order_by(Product.average_rating.desc(), Product.deal_score.desc()).limit(limit).all()

            results = []
            for c in candidates:
                diff_price = round(c.current_best_price - baseline_price, 2)
                results.append({
                    "product": c,
                    "price_tier": "premium",
                    "confidence": 0.90,
                    "price_difference": diff_price,
                    "reason": f"Premium hardware upgrade for +${diff_price} price delta"
                })
            return results
        except Exception as e:
            logger.error(f"Error computing premium upgrades for product {product.id}: {e}")
            return []
