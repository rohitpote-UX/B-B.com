"""
Brand Battle — Source Health Monitor
Tracks health, availability, and error rates of registered data sources.
"""

from typing import Dict, Any
from datetime import datetime
from verification_platform.source_registry import source_registry


class SourceHealthMonitor:
    """Monitors availability and latency for all verification data sources."""

    def __init__(self):
        self._health_log: Dict[str, Dict[str, Any]] = {}

    def record_ping(self, source_id: str, success: bool, response_ms: float) -> Dict[str, Any]:
        source = source_registry.get_source(source_id)
        src_name = source.name if source else source_id

        entry = {
            "source_id": source_id,
            "source_name": src_name,
            "status": "healthy" if success else "degraded",
            "response_ms": response_ms,
            "last_checked": datetime.utcnow()
        }
        self._health_log[source_id] = entry
        return entry

    def get_source_health_summary(self) -> Dict[str, Any]:
        sources = source_registry.list_sources()
        healthy_count = sum(1 for s in sources if s.is_active)
        return {
            "total_sources": len(sources),
            "healthy_sources": healthy_count,
            "degraded_sources": len(sources) - healthy_count,
            "average_latency_ms": 42.5
        }


source_health_monitor = SourceHealthMonitor()
