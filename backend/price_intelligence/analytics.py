"""
Brand Battle — Price Intelligence Analytics Tracker
Tracks price movements, savings generated for users, and opportunity distribution.
"""

from typing import Dict, Any, List
from collections import Counter, deque
from datetime import datetime, timezone


class PriceIntelligenceAnalytics:
    """Analytics aggregator for market opportunity trends."""

    def __init__(self, max_history: int = 2000):
        self._price_drops: deque = deque(maxlen=max_history)
        self._opportunity_scores: Counter = Counter()

    def record_price_drop(self, product_id: int, old_price: float, new_price: float) -> None:
        drop_amt = old_price - new_price
        drop_pct = (drop_amt / old_price) * 100
        self._price_drops.append({
            "product_id": product_id,
            "old_price": old_price,
            "new_price": new_price,
            "savings": drop_amt,
            "drop_pct": round(drop_pct, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_analytics_summary(self) -> Dict[str, Any]:
        recent = list(self._price_drops)
        total_drops = len(recent)
        total_savings = sum(d["savings"] for d in recent)
        avg_drop_pct = (sum(d["drop_pct"] for d in recent) / total_drops) if total_drops > 0 else 0.0

        return {
            "total_price_drops_tracked": total_drops,
            "total_user_savings_identified": round(total_savings, 2),
            "average_price_drop_pct": round(avg_drop_pct, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Singleton
price_intel_analytics = PriceIntelligenceAnalytics()
