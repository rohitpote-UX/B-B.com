"""
Brand Battle — 20. Happiness Score & Feedback Engine
Tracks user feedback (helpful vs unhelpful votes) and optimizes system toward Happiness Index.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from notification_platform.repository import notification_repo
from notification_platform.analytics import notification_analytics


class HappinessFeedbackEngine:
    """Collects notification feedback and tracks Happiness Index."""

    def record_user_feedback(
        self,
        db: Session,
        user_id: int,
        notification_id: int,
        is_helpful: bool,
        feedback_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record helpfulness feedback."""
        fb = notification_repo.record_feedback(
            db=db,
            user_id=user_id,
            notification_id=notification_id,
            is_helpful=is_helpful,
            feedback_text=feedback_text,
        )

        metrics = notification_analytics.calculate_happiness_metric(db)

        return {
            "feedback_id": fb.id,
            "is_helpful": is_helpful,
            "current_happiness_index_pct": metrics["happiness_index_pct"],
        }


# Singleton
happiness_feedback_engine = HappinessFeedbackEngine()
