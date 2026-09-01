"""
Brand Battle — Notification History Audit Module
Maintains immutable history of sent notifications.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from notification_platform.repository import notification_repo


class NotificationHistoryModule:
    """Manages audit log queries for notification history."""

    def get_history(self, db: Session, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
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


# Singleton
notification_history_module = NotificationHistoryModule()
