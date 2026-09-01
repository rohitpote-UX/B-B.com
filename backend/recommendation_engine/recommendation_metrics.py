"""
Brand Battle — Recommendation Observability & Metrics Engine
Tracks response latency, cache hit rates, CTR, diversity, accuracy, and algorithm performance.
"""

from typing import Dict, Any
import time
from collections import deque


class RecommendationMetrics:
    """In-memory metrics accumulator for monitoring recommendation platform health."""

    def __init__(self):
        self._total_requests: int = 0
        self._cache_hits: int = 0
        self._latencies: deque = deque(maxlen=1000)
        self._recommendations_generated: int = 0
        self._clicks_count: int = 0

    def record_request(self, latency_ms: float, cache_hit: bool = False, count: int = 0):
        """Record recommendation evaluation telemetry."""
        self._total_requests += 1
        if cache_hit:
            self._cache_hits += 1
        self._latencies.append(latency_ms)
        self._recommendations_generated += count

    def record_click(self):
        """Record implicit recommendation click-through."""
        self._clicks_count += 1

    def get_telemetry_summary(self) -> Dict[str, Any]:
        """Compile observational metrics summary."""
        avg_latency = (sum(self._latencies) / len(self._latencies)) if self._latencies else 0.0
        hit_ratio = (self._cache_hits / self._total_requests) if self._total_requests else 0.0
        ctr = (self._clicks_count / max(1, self._recommendations_generated))

        return {
            "total_requests": self._total_requests,
            "cache_hits": self._cache_hits,
            "cache_hit_ratio": round(hit_ratio, 4),
            "average_latency_ms": round(avg_latency, 2),
            "total_recommendations_generated": self._recommendations_generated,
            "recorded_clicks": self._clicks_count,
            "click_through_rate": round(ctr, 4)
        }


recommendation_metrics_collector = RecommendationMetrics()
