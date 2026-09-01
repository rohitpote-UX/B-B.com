"""
Brand Battle — 1. AI Relevance Engine
Calculates composite relevance score (0-1.0) based on intent, price drop depth, and brand affinity. Gated delivery >0.70.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product, User
from notification_platform.config import notification_config


class AIRelevanceEngine:
    """Calculates AI Relevance Score for every candidate notification."""

    def calculate_relevance(
        self,
        db: Session,
        user_id: int,
        event_type: str,
        product: Optional[Product] = None,
        price_drop_pct: float = 0.0,
        opportunity_score: float = 0.0,
    ) -> float:
        """Compute composite 0-1.0 AI Relevance Score."""
        weights = notification_config.weights

        # 1. Price drop signal (max 1.0)
        drop_signal = min(1.0, price_drop_pct / 30.0)

        # 2. Opportunity score signal (max 1.0)
        opp_signal = opportunity_score / 100.0 if opportunity_score > 0 else 0.5

        # 3. Intent signal by event type
        if event_type in ["price_drop", "buy_now", "wishlist_drop"]:
            intent_signal = 0.95
        elif event_type in ["opportunity_alert", "restock"]:
            intent_signal = 0.85
        elif event_type in ["celebration", "daily_digest"]:
            intent_signal = 0.90
        else:
            intent_signal = 0.60

        # Composite Relevance Calculation
        score = (
            intent_signal * weights.intent_weight
            + drop_signal * weights.price_drop_depth_weight
            + opp_signal * weights.opportunity_score_weight
            + 0.85 * weights.user_brand_affinity_weight
            + 0.90 * weights.recency_weight
        )

        return round(min(1.0, max(0.0, score)), 2)

    def is_relevant(self, score: float) -> bool:
        """Threshold check: delivers only if score >= configurable threshold (default 0.70)."""
        return score >= notification_config.relevance_threshold


# Singleton
ai_relevance_engine = AIRelevanceEngine()
