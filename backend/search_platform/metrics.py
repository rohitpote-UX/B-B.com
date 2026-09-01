"""
Brand Battle — Search Observability Metrics
Per-request latency tracking, cache hit counters, error rates, and query volume.
"""

import time
import logging
from typing import Dict, Any
from collections import deque
from datetime import datetime, timezone

logger = logging.getLogger("brandbattle.search.metrics")


class SearchMetricsCollector:
    """In-memory observability metrics for the search platform."""

    def __init__(self, max_latencies: int = 5000):
        self._latencies: deque = deque(maxlen=max_latencies)
        self._parse_latencies: deque = deque(maxlen=max_latencies)
        self._retrieval_latencies: deque = deque(maxlen=max_latencies)
        self._ranking_latencies: deque = deque(maxlen=max_latencies)
        self._reranking_latencies: deque = deque(maxlen=max_latencies)
        self._total_requests: int = 0
        self._cache_hits: int = 0
        self._errors: int = 0
        self._autocomplete_requests: int = 0
        self._autocomplete_latencies: deque = deque(maxlen=2000)

    def record_search_request(
        self,
        total_ms: float,
        parse_ms: float = 0.0,
        retrieval_ms: float = 0.0,
        ranking_ms: float = 0.0,
        reranking_ms: float = 0.0,
        cache_hit: bool = False,
    ) -> None:
        """Record a search request with detailed latency breakdown."""
        self._total_requests += 1
        self._latencies.append(total_ms)
        if parse_ms > 0:
            self._parse_latencies.append(parse_ms)
        if retrieval_ms > 0:
            self._retrieval_latencies.append(retrieval_ms)
        if ranking_ms > 0:
            self._ranking_latencies.append(ranking_ms)
        if reranking_ms > 0:
            self._reranking_latencies.append(reranking_ms)
        if cache_hit:
            self._cache_hits += 1

    def record_autocomplete_request(self, latency_ms: float) -> None:
        """Record an autocomplete request latency."""
        self._autocomplete_requests += 1
        self._autocomplete_latencies.append(latency_ms)

    def record_error(self) -> None:
        """Record a search error."""
        self._errors += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        latencies = list(self._latencies)
        ac_latencies = list(self._autocomplete_latencies)

        return {
            "search": {
                "total_requests": self._total_requests,
                "cache_hits": self._cache_hits,
                "cache_hit_ratio": round(self._cache_hits / max(1, self._total_requests) * 100, 2),
                "errors": self._errors,
                "error_rate": round(self._errors / max(1, self._total_requests) * 100, 2),
                "latency": self._compute_latency_stats(latencies),
                "breakdown": {
                    "parse": self._compute_latency_stats(list(self._parse_latencies)),
                    "retrieval": self._compute_latency_stats(list(self._retrieval_latencies)),
                    "ranking": self._compute_latency_stats(list(self._ranking_latencies)),
                    "reranking": self._compute_latency_stats(list(self._reranking_latencies)),
                },
            },
            "autocomplete": {
                "total_requests": self._autocomplete_requests,
                "latency": self._compute_latency_stats(ac_latencies),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _compute_latency_stats(self, latencies: list) -> Dict[str, float]:
        """Compute latency statistics."""
        if not latencies:
            return {"avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        return {
            "avg_ms": round(sum(sorted_latencies) / n, 2),
            "p50_ms": round(sorted_latencies[n // 2], 2),
            "p95_ms": round(sorted_latencies[int(n * 0.95)], 2) if n > 1 else round(sorted_latencies[0], 2),
            "p99_ms": round(sorted_latencies[int(n * 0.99)], 2) if n > 1 else round(sorted_latencies[0], 2),
            "min_ms": round(sorted_latencies[0], 2),
            "max_ms": round(sorted_latencies[-1], 2),
        }


# Singleton
search_metrics = SearchMetricsCollector()
