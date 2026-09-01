"""
Brand Battle — Search Analytics Engine
Tracks search performance, zero-result rates, top searches, and conversion metrics.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from collections import Counter, deque
from datetime import datetime, timezone

logger = logging.getLogger("brandbattle.search.analytics")


class SearchAnalytics:
    """In-memory search analytics tracker for dashboards and observability."""

    def __init__(self, max_events: int = 10000):
        self._search_events: deque = deque(maxlen=max_events)
        self._top_queries: Counter = Counter()
        self._zero_result_queries: Counter = Counter()
        self._filter_usage: Counter = Counter()
        self._click_events: deque = deque(maxlen=5000)
        self._total_searches: int = 0
        self._total_zero_results: int = 0
        self._total_clicks: int = 0

    def record_search(
        self,
        query: str,
        results_count: int,
        latency_ms: float,
        filters: Optional[Dict] = None,
        was_corrected: bool = False,
        cache_hit: bool = False,
    ) -> None:
        """Record a search event for analytics."""
        self._total_searches += 1
        self._top_queries[query.lower().strip()] += 1

        event = {
            "query": query,
            "results_count": results_count,
            "latency_ms": round(latency_ms, 2),
            "filters": filters,
            "was_corrected": was_corrected,
            "cache_hit": cache_hit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._search_events.append(event)

        if results_count == 0:
            self._total_zero_results += 1
            self._zero_result_queries[query.lower().strip()] += 1

        if filters:
            for key in filters:
                self._filter_usage[key] += 1

    def record_click(self, query: str, product_id: int, position: int) -> None:
        """Record a search result click event."""
        self._total_clicks += 1
        self._click_events.append({
            "query": query,
            "product_id": product_id,
            "position": position,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        # Calculate averages from recent events
        recent_events = list(self._search_events)[-1000:]
        avg_latency = 0.0
        avg_results = 0.0
        cache_hits = 0
        corrections = 0

        if recent_events:
            avg_latency = sum(e["latency_ms"] for e in recent_events) / len(recent_events)
            avg_results = sum(e["results_count"] for e in recent_events) / len(recent_events)
            cache_hits = sum(1 for e in recent_events if e.get("cache_hit"))
            corrections = sum(1 for e in recent_events if e.get("was_corrected"))

        zero_result_rate = (
            self._total_zero_results / self._total_searches * 100
            if self._total_searches > 0 else 0.0
        )

        ctr = (
            self._total_clicks / self._total_searches * 100
            if self._total_searches > 0 else 0.0
        )

        cache_hit_ratio = (
            cache_hits / len(recent_events) * 100
            if recent_events else 0.0
        )

        return {
            "total_searches": self._total_searches,
            "total_zero_results": self._total_zero_results,
            "zero_result_rate": round(zero_result_rate, 2),
            "total_clicks": self._total_clicks,
            "click_through_rate": round(ctr, 2),
            "average_latency_ms": round(avg_latency, 2),
            "average_results_count": round(avg_results, 1),
            "cache_hit_ratio": round(cache_hit_ratio, 2),
            "total_corrections": corrections,
            "top_searches": [
                {"query": q, "count": c}
                for q, c in self._top_queries.most_common(20)
            ],
            "top_zero_result_queries": [
                {"query": q, "count": c}
                for q, c in self._zero_result_queries.most_common(10)
            ],
            "filter_usage": dict(self._filter_usage.most_common(15)),
        }


# Singleton
search_analytics = SearchAnalytics()
