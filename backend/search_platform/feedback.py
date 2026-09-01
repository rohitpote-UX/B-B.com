"""
Brand Battle — Search Feedback Collector
Tracks click events, query reformulations, and filter usage for ranking improvement.
"""

import logging
from typing import Dict, Any, Optional, List
from collections import deque, Counter
from datetime import datetime, timezone

logger = logging.getLogger("brandbattle.search.feedback")


class SearchFeedbackCollector:
    """Collects implicit search feedback signals for ranking optimization."""

    def __init__(self, max_events: int = 5000):
        self._click_events: deque = deque(maxlen=max_events)
        self._reformulation_events: deque = deque(maxlen=2000)
        self._filter_events: deque = deque(maxlen=2000)
        self._product_click_counts: Counter = Counter()

    def record_click(
        self,
        query: str,
        product_id: int,
        position: int,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Record a click on a search result."""
        self._click_events.append({
            "query": query,
            "product_id": product_id,
            "position": position,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._product_click_counts[product_id] += 1

    def record_reformulation(
        self,
        original_query: str,
        new_query: str,
        user_id: Optional[int] = None,
    ) -> None:
        """Record a query reformulation (user changed their search)."""
        self._reformulation_events.append({
            "original_query": original_query,
            "new_query": new_query,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_filter_usage(
        self,
        query: str,
        filter_key: str,
        filter_value: str,
    ) -> None:
        """Record filter/facet selection."""
        self._filter_events.append({
            "query": query,
            "filter_key": filter_key,
            "filter_value": filter_value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_product_click_score(self, product_id: int) -> float:
        """Get normalized click-through score for a product (0-1)."""
        clicks = self._product_click_counts.get(product_id, 0)
        if clicks <= 0:
            return 0.0
        # Log normalization
        import math
        return min(1.0, math.log10(clicks + 1) / 3.0)

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get feedback collection summary."""
        return {
            "total_clicks": len(self._click_events),
            "total_reformulations": len(self._reformulation_events),
            "total_filter_events": len(self._filter_events),
            "top_clicked_products": [
                {"product_id": pid, "clicks": count}
                for pid, count in self._product_click_counts.most_common(20)
            ],
        }


# Singleton
search_feedback = SearchFeedbackCollector()
