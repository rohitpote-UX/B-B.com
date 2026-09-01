"""
Brand Battle — Quiet Hours Engine
Enforces DND and quiet hours rules (default 22:00–07:00).
"""

from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from notification_platform.repository import notification_repo
from notification_platform.config import notification_config


class QuietHoursEngine:
    """Enforces Quiet Hours & DND delivery rules."""

    def is_in_quiet_hours(self, db: Session, user_id: int) -> bool:
        """Check if current time is within user quiet hours."""
        prefs = notification_repo.get_or_create_preferences(db, user_id)
        now = datetime.now(timezone.utc)
        current_hour = now.hour

        start = prefs.quiet_hours_start
        end = prefs.quiet_hours_end

        if start > end:
            # Spans midnight (e.g. 22:00 to 07:00)
            return current_hour >= start or current_hour < end
        else:
            return start <= current_hour < end


# Singleton
quiet_hours_engine = QuietHoursEngine()
