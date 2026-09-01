"""
Brand Battle — 1. Historical Price Timeline Engine
Maintains complete historical price records (24h, 7d, 30d, 90d, 6m, 1y, lifetime) with immutable snapshots.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from models import Product
from price_intelligence.repository import price_intel_repo
from price_intelligence.utils import mean, stddev


class HistoricalPriceTimelineEngine:
    """Computes price timeline windows and statistical benchmarks."""

    def get_timeline_summary(self, db: Session, product: Product) -> Dict[str, Any]:
        """Compute 24h, 7d, 30d, 90d, 6m, 1y, and lifetime historical price metrics."""
        snapshots = price_intel_repo.get_price_history_snapshots(db, product.id, days=365)
        current_price = product.current_best_price or product.lowest_price or 0.0

        if not snapshots:
            return {
                "h24_lowest": current_price,
                "d7_lowest": current_price,
                "d30_lowest": current_price,
                "d90_lowest": current_price,
                "m6_lowest": current_price,
                "y1_lowest": current_price,
                "lifetime_lowest": product.lowest_price or current_price,
                "lifetime_highest": product.highest_price or current_price,
                "average_price": current_price,
                "snapshot_count": 0,
            }

        prices = [s.effective_final_price for s in snapshots]
        now = datetime.now(timezone.utc)

        def get_min_in_days(days: int) -> float:
            cutoff = now - timedelta(days=days)
            filtered = []
            for s in snapshots:
                created_at = s.created_at
                if created_at and created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if created_at and created_at >= cutoff:
                    filtered.append(s.effective_final_price)
            return min(filtered) if filtered else current_price

        return {
            "h24_lowest": get_min_in_days(1),
            "d7_lowest": get_min_in_days(7),
            "d30_lowest": get_min_in_days(30),
            "d90_lowest": get_min_in_days(90),
            "m6_lowest": get_min_in_days(180),
            "y1_lowest": get_min_in_days(365),
            "lifetime_lowest": min(min(prices), product.lowest_price or current_price),
            "lifetime_highest": max(max(prices), product.highest_price or current_price),
            "average_price": round(mean(prices), 2),
            "snapshot_count": len(snapshots),
        }


# Singleton
price_history_engine = HistoricalPriceTimelineEngine()
