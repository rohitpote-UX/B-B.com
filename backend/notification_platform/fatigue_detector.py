"""
Brand Battle — 3. Notification Fatigue Detector
Tracks open/dismiss/mute rate and automatically throttles frequency if fatigue score rises.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from notification_platform.repository import notification_repo
from notification_platform.config import notification_config


class NotificationFatigueDetector:
    """Calculates real-time notification fatigue score and throttles delivery."""

    def evaluate_fatigue(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Compute user fatigue score and determine if delivery should be throttled."""
        profile = notification_repo.get_fatigue_profile(db, user_id)

        open_rate = profile.open_count_7d / max(1, (profile.open_count_7d + profile.dismissal_count_7d))
        dismiss_rate = 1.0 - open_rate

        # Fatigue score (0-1.0)
        fatigue_score = round(min(1.0, (profile.dismissal_count_7d * 0.2) + (dismiss_rate * 0.5)), 2)

        should_throttle = (
            fatigue_score > notification_config.fatigue.fatigue_score_threshold
            or profile.dismissal_count_7d >= notification_config.fatigue.max_dismissals_before_throttle
        )

        return {
            "fatigue_score": fatigue_score,
            "should_throttle": should_throttle,
            "max_allowed_today": 1 if should_throttle else notification_config.fatigue.max_notifications_per_day,
        }


# Singleton
fatigue_detector = NotificationFatigueDetector()
