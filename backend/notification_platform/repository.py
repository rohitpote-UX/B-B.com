"""
Brand Battle — Notification Platform Repository Layer
Database access layer following the Repository Pattern for preferences, history, digests, and feedback.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from notification_platform.models import (
    NotificationEvent, NotificationPreference, NotificationHistory,
    NotificationDigest, FatigueProfile, NotificationFeedback
)


class NotificationRepository:
    """Repository managing all database operations for the Notification Platform."""

    def get_or_create_preferences(self, db: Session, user_id: int) -> NotificationPreference:
        """Fetch user preferences or initialize defaults."""
        prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        return prefs

    def update_preferences(self, db: Session, user_id: int, updates: Dict[str, Any]) -> NotificationPreference:
        """Update user preferences."""
        prefs = self.get_or_create_preferences(db, user_id)
        for key, value in updates.items():
            if hasattr(prefs, key) and value is not None:
                setattr(prefs, key, value)
        db.commit()
        db.refresh(prefs)
        return prefs

    def record_delivered_notification(
        self,
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        body: str,
        product_id: Optional[int] = None,
        channel: str = "in_app",
        relevance_score: float = 0.85,
    ) -> NotificationHistory:
        """Log a delivered notification into history."""
        record = NotificationHistory(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            product_id=product_id,
            channel=channel,
            relevance_score=relevance_score,
            is_read=False,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_user_notifications(self, db: Session, user_id: int, limit: int = 20) -> List[NotificationHistory]:
        """Fetch user in-app notification history."""
        return (
            db.query(NotificationHistory)
            .filter(NotificationHistory.user_id == user_id)
            .order_by(desc(NotificationHistory.delivered_at))
            .limit(limit)
            .all()
        )

    def mark_as_read(self, db: Session, user_id: int, notification_id: int) -> bool:
        """Mark notification as read (Cross-device sync)."""
        record = (
            db.query(NotificationHistory)
            .filter(
                NotificationHistory.id == notification_id,
                NotificationHistory.user_id == user_id,
            )
            .first()
        )
        if record:
            record.is_read = True
            record.read_at = datetime.now(timezone.utc)
            db.commit()
            return True
        return False

    def get_fatigue_profile(self, db: Session, user_id: int) -> FatigueProfile:
        """Fetch or initialize user fatigue profile."""
        profile = db.query(FatigueProfile).filter(FatigueProfile.user_id == user_id).first()
        if not profile:
            profile = FatigueProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    def record_feedback(
        self, db: Session, user_id: int, notification_id: int, is_helpful: bool, feedback_text: Optional[str] = None
    ) -> NotificationFeedback:
        """Record notification feedback for Happiness Score calculation."""
        fb = NotificationFeedback(
            notification_id=notification_id,
            user_id=user_id,
            is_helpful=is_helpful,
            feedback_text=feedback_text,
        )
        db.add(fb)
        db.commit()
        db.refresh(fb)
        return fb


# Singleton
notification_repo = NotificationRepository()
