"""
Brand Battle — Freshness Engine
Tracks data freshness, time decay, and determines stale verification statuses.
"""

from datetime import datetime, timezone, timedelta
from typing import Tuple


class FreshnessEngine:
    """Evaluates data freshness and decay rates for product verification."""

    def evaluate_freshness(self, last_verified: datetime) -> Tuple[float, str]:
        """
        Returns (freshness_hours, freshness_status).
        Status: 'Fresh' (<24h), 'Moderate' (24h-72h), 'Stale' (>72h).
        """
        now = datetime.now(timezone.utc)
        if last_verified.tzinfo is None:
            last_verified = last_verified.replace(tzinfo=timezone.utc)

        delta = now - last_verified
        hours = max(0.0, delta.total_seconds() / 3600.0)

        if hours <= 24.0:
            status = "Fresh"
        elif hours <= 72.0:
            status = "Moderate"
        else:
            status = "Stale"

        return (round(hours, 1), status)

    def apply_time_decay(self, base_confidence: float, hours_old: float) -> float:
        """Applies slight time decay to old verification claims (decay cap at 15%)."""
        if hours_old <= 24.0:
            return base_confidence
        
        days_old = (hours_old - 24.0) / 24.0
        decay = min(15.0, days_old * 0.5)
        
        return round(max(50.0, base_confidence - decay), 1)


freshness_engine = FreshnessEngine()
