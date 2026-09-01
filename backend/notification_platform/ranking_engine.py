"""
Brand Battle — 19. Notification Ranking Engine
Prioritizes and ranks candidate notifications so only the highest-value items are delivered.
"""

from typing import List, Dict, Any


class NotificationRankingEngine:
    """Ranks candidate notification events by relevance, urgency, and value."""

    PRIORITY_MAP = {
        "price_drop": 1,
        "buy_now": 1,
        "opportunity_alert": 2,
        "wishlist_drop": 2,
        "celebration": 3,
        "daily_digest": 3,
        "educational": 4,
        "general": 5,
    }

    def rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort candidates by priority level and relevance score."""

        def get_sort_key(item: Dict[str, Any]):
            event_type = item.get("event_type", "general")
            priority = self.PRIORITY_MAP.get(event_type, 5)
            rel_score = item.get("relevance_score", 0.0)
            return (priority, -rel_score)

        return sorted(candidates, key=get_sort_key)


# Singleton
notification_ranking_engine = NotificationRankingEngine()
