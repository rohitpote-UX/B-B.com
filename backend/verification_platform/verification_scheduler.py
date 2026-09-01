"""
Brand Battle — Verification Scheduler
Manages automatic periodic re-verification tiers.
"""

from typing import Dict, Any, List
from datetime import datetime


class VerificationScheduler:
    """Manages tiered product re-verification intervals."""

    INTERVALS_HOURS = {
        "high_traffic": 6,
        "popular": 12,
        "medium": 24,
        "long_tail": 168,  # Weekly
        "discontinued": 720  # Monthly
    }

    def get_schedule_tier(self, product_reviews_count: int = 100) -> str:
        if product_reviews_count >= 10000:
            return "high_traffic"
        elif product_reviews_count >= 1000:
            return "popular"
        elif product_reviews_count >= 100:
            return "medium"
        return "long_tail"

    def is_due_for_reverification(self, last_verified: datetime, tier: str) -> bool:
        interval = self.INTERVALS_HOURS.get(tier, 24)
        hours_since = (datetime.utcnow() - last_verified).total_seconds() / 3600.0
        return hours_since >= interval


verification_scheduler = VerificationScheduler()
