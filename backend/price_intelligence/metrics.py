"""
Brand Battle — Price Intelligence Observability Metrics
Prometheus-compatible telemetry tracking request latency, cache hit ratios, forecast accuracy, and alert triggers.
"""

from typing import Dict, Any
from collections import deque
from datetime import datetime, timezone


class PriceIntelligenceMetricsCollector:
    """In-memory telemetry collector for observability and health monitoring."""

    def __init__(self, max_samples: int = 5000):
        self._latencies: deque = deque(maxlen=max_samples)
        self._total_requests: int = 0
        self._cache_hits: int = 0
        self._alerts_triggered: int = 0
        self._fake_discounts_flagged: int = 0

    def record_request(self, latency_ms: float, cache_hit: bool = False) -> None:
        self._total_requests += 1
        self._latencies.append(latency_ms)
        if cache_hit:
            self._cache_hits += 1

    def record_alert_triggered(self) -> None:
        self._alerts_triggered += 1

    def record_fake_discount_flagged(self) -> None:
        self._fake_discounts_flagged += 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        latencies = sorted(list(self._latencies))
        n = len(latencies)
        avg_ms = round(sum(latencies) / n, 2) if n > 0 else 0.0
        p95_ms = round(latencies[int(n * 0.95)], 2) if n > 1 else avg_ms

        cache_ratio = round(self._cache_hits / max(1, self._total_requests) * 100, 2)

        return {
            "total_requests": self._total_requests,
            "cache_hits": self._cache_hits,
            "cache_hit_ratio_pct": cache_ratio,
            "average_latency_ms": avg_ms,
            "p95_latency_ms": p95_ms,
            "alerts_triggered": self._alerts_triggered,
            "fake_discounts_flagged": self._fake_discounts_flagged,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Singleton
price_intel_metrics = PriceIntelligenceMetricsCollector()
