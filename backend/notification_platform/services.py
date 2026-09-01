"""
Brand Battle — Enterprise Notification Platform Service Facade
High-level service facade unifying all 20 Notification Platform modules.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models import User, Product
from notification_platform.repository import notification_repo
from notification_platform.digest_generator import digest_generator
from notification_platform.celebration_engine import celebration_engine
from notification_platform.notification_engine import master_notification_pipeline
from notification_platform.feedback_engine import happiness_feedback_engine
from notification_platform.analytics import notification_analytics
from notification_platform.cross_device_sync import cross_device_sync_engine

logger = logging.getLogger("brandbattle.notification_platform.service")


class NotificationPlatformService:
    """High-level service facade for notification feed, digests, preferences, and feedback."""

    def get_user_feed(self, db: Session, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch user in-app notification feed."""
        records = notification_repo.get_user_notifications(db, user_id, limit=limit)
        return [
            {
                "id": r.id,
                "notification_type": r.notification_type,
                "title": r.title,
                "body": r.body,
                "product_id": r.product_id,
                "channel": r.channel,
                "relevance_score": r.relevance_score,
                "is_read": r.is_read,
                "delivered_at": r.delivered_at.isoformat(),
            }
            for r in records
        ]

    def mark_notification_read(self, db: Session, user_id: int, notification_id: int) -> Dict[str, Any]:
        """Mark notification as read (Cross-device sync)."""
        return cross_device_sync_engine.sync_read_status(db, user_id, notification_id)

    def get_daily_digest(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Generate or fetch Daily AI Digest summary."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, username="Shopper", email="user@brandbattle.com")

        digest = digest_generator.generate_digest(db, user)
        return digest.model_dump()

    def update_user_preferences(self, db: Session, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preference center settings."""
        prefs = notification_repo.update_preferences(db, user_id, updates)
        return {
            "user_id": user_id,
            "enable_in_app": prefs.enable_in_app,
            "enable_email": prefs.enable_email,
            "enable_push": prefs.enable_push,
            "enable_daily_digest": prefs.enable_daily_digest,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "max_daily_notifications": prefs.max_daily_notifications,
        }

    def record_feedback(
        self, db: Session, user_id: int, notification_id: int, is_helpful: bool, feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit feedback for Happiness Index calculation."""
        return happiness_feedback_engine.record_user_feedback(
            db=db,
            user_id=user_id,
            notification_id=notification_id,
            is_helpful=is_helpful,
            feedback_text=feedback_text,
        )


# Singleton
notification_platform_service = NotificationPlatformService()
