"""
Brand Battle — 3. User Journey Intelligence Engine
Tracks complete end-to-end user decision journeys (Landing -> Search -> View -> Compare -> Rec -> Wishlist -> Alert -> Buy Intent).
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from analytics_platform.models import AnalyticsEvent


class UserJourneyIntelligenceEngine:
    """Reconstructs user decision journeys and identifies success paths vs drop-offs."""

    JOURNEY_STAGES = [
        "landing",
        "search",
        "product_view",
        "comparison",
        "recommendation",
        "wishlist",
        "price_alert",
        "buy_intent",
    ]

    def reconstruct_journey(self, db: Session, session_id: str) -> Dict[str, Any]:
        """Reconstruct user journey steps from event log."""
        events = (
            db.query(AnalyticsEvent)
            .filter(AnalyticsEvent.session_id == session_id)
            .order_by(AnalyticsEvent.created_at)
            .all()
        )

        stages_visited = [e.event_category for e in events]
        has_buy_intent = "buy_intent" in stages_visited or "price_alert" in stages_visited

        return {
            "session_id": session_id,
            "total_steps": len(events),
            "stages_visited": list(set(stages_visited)),
            "converted_to_intent": has_buy_intent,
            "drop_off_stage": stages_visited[-1] if stages_visited else "landing",
        }


# Singleton
user_journey_engine = UserJourneyIntelligenceEngine()
