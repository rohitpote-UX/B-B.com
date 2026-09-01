"""
Brand Battle — Scoring Engine
Provides normalized component scoring functions for evaluating recommendation signals.
"""

from typing import Dict, Any, Optional
from models import Product


class ScoringEngine:
    """Individual normalized scoring metrics for recommendation candidate evaluation."""

    def normalize_score(self, val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Normalize any metric scale to [0.0, 1.0]."""
        if max_val <= min_val:
            return 0.0
        normalized = (val - min_val) / (max_val - min_val)
        return round(max(0.0, min(1.0, normalized)), 4)

    def evaluate_price_alignment(self, target_price: float, candidate_price: float) -> float:
        """Evaluate how closely candidate price aligns with baseline price."""
        if not target_price or not candidate_price:
            return 0.5
        ratio = candidate_price / target_price
        if 0.8 <= ratio <= 1.2:
            return 1.0
        elif 0.6 <= ratio <= 1.5:
            return 0.75
        elif 0.4 <= ratio <= 2.0:
            return 0.50
        return 0.25

    def evaluate_brand_trust(self, product: Product) -> float:
        """Evaluate brand reliability and trust score."""
        if hasattr(product, 'brand') and product.brand and hasattr(product.brand, 'trust_score'):
            return self.normalize_score(product.brand.trust_score or 5.0, 0.0, 10.0)
        return 0.70

    def evaluate_popularity(self, product: Product) -> float:
        """Evaluate normalized popularity score based on view count and review volume."""
        views = getattr(product, 'view_count', 0) or 0
        reviews = getattr(product, 'total_reviews', 0) or 0
        score = min(1.0, (views * 0.01 + reviews * 0.05) / 100.0)
        return round(score, 4)
