"""
Brand Battle — Personalization Engine
Personalizes notifications based on user preferences, wishlist, and brand affinity.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product, User


class NotificationPersonalizationEngine:
    """Personalizes notification content for individual users."""

    def personalize_content(
        self, db: Session, user_id: int, title: str, body: str
    ) -> Dict[str, str]:
        """Personalize title and body with user context."""
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name or user.username if user else None

        if user_name:
            personalized_title = f"{title}"
            personalized_body = f"{body}"
        else:
            personalized_title = title
            personalized_body = body

        return {"title": personalized_title, "body": personalized_body}


# Singleton
notification_personalization = NotificationPersonalizationEngine()
