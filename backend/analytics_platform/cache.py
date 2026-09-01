"""
Brand Battle — Analytics Platform Redis Stream & Cache Layer
Redis Streams for real-time streaming analytics (<20ms ingestion) and cached dashboard snapshots.
"""

from typing import Any, Optional, Dict
from redis_client import get_cache, set_cache, redis_client, is_redis_healthy
from analytics_platform.config import analytics_config

_PREFIX_DASHBOARD = "analytics:dashboard:snapshot"


class AnalyticsCache:
    """Redis stream manager and cache provider for analytics."""

    def push_to_stream(self, event_data: Dict[str, Any]) -> bool:
        """Push structured event to Redis Stream for real-time processing (<20ms target)."""
        if not analytics_config.enable_redis_stream:
            return False
        if redis_client and is_redis_healthy():
            try:
                redis_client.xadd(
                    analytics_config.stream.stream_name,
                    event_data,
                    maxlen=analytics_config.stream.max_len,
                )
                return True
            except Exception:
                return False
        return False

    def get_dashboard_snapshot(self) -> Optional[Any]:
        if not analytics_config.enable_redis_stream:
            return None
        return get_cache(_PREFIX_DASHBOARD)

    def set_dashboard_snapshot(self, data: Any) -> bool:
        if not analytics_config.enable_redis_stream:
            return False
        return set_cache(_PREFIX_DASHBOARD, data, ttl=300)


# Singleton
analytics_cache = AnalyticsCache()
