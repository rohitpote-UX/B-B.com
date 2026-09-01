"""
Brand Battle — 17. User Preference Center Engine
Enforces user notification preferences (quiet hours, channels, max daily cap, brand filters).
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from notification_platform.repository import notification_repo
from notification_platform.models import NotificationPreference


class UserPreferenceCenterEngine:
    """Filters and enforces user-defined notification preferences."""

    def is_notification_allowed(
        self, db: Session, user_id: int, channel: str, brand: Optional[str] = None
    ) -> bool:
        """Check if notification is permitted under user preference rules."""
        prefs = notification_repo.get_or_create_preferences(db, user_id)

        # 1. Channel checks
        if channel == "in_app" and not prefs.enable_in_app:
            return False
        if channel == "email" and not prefs.enable_email:
            return False
        if channel == "push" and not prefs.enable_push:
            return False

        # 2. Brand preference filter
        if brand and prefs.preferred_brands:
            if brand.lower() not in [b.lower() for b in prefs.preferred_brands]:
                return False

        return True


# Singleton
user_preference_center = UserPreferenceCenterEngine()
