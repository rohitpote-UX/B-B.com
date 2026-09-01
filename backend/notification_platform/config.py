"""
Brand Battle — Enterprise AI Notification Intelligence Configuration
Centralized thresholds, fatigue caps, quiet hours defaults, relevance weights, and delivery SLOs.
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class RelevanceWeights(BaseModel):
    """Weights for calculating AI Notification Relevance Score (0-1.0)."""
    intent_weight: float = 0.30
    price_drop_depth_weight: float = 0.25
    opportunity_score_weight: float = 0.20
    user_brand_affinity_weight: float = 0.15
    recency_weight: float = 0.10


class FatigueConfig(BaseModel):
    """Fatigue detection thresholds & max daily caps."""
    max_notifications_per_day: int = 3
    fatigue_score_threshold: float = 0.65  # >0.65 reduces frequency
    max_dismissals_before_throttle: int = 3


class QuietHoursConfig(BaseModel):
    """Default quiet hours settings (DND)."""
    enabled: bool = True
    start_hour: int = 22  # 10:00 PM
    end_hour: int = 7     # 7:00 AM


class NotificationPlatformConfig(BaseModel):
    """Master configuration for the Notification Intelligence Platform."""
    enabled: bool = True
    algorithm_version: str = "v6.0.0-enterprise-notification-intelligence"
    relevance_threshold: float = 0.70     # Only deliver if score >= 0.70
    meaningful_price_drop_min_inr: float = 1000.0
    meaningful_price_drop_min_pct: float = 10.0
    opportunity_score_threshold: float = 85.0

    weights: RelevanceWeights = RelevanceWeights()
    fatigue: FatigueConfig = FatigueConfig()
    quiet_hours: QuietHoursConfig = QuietHoursConfig()

    # Feature flags
    enable_redis_cache: bool = True
    enable_daily_digest: bool = True
    enable_fatigue_throttling: bool = True
    enable_cross_device_sync: bool = True
    enable_happiness_score: bool = True


notification_config = NotificationPlatformConfig()
