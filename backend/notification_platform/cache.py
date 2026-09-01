"""
Brand Battle — Notification Platform Redis Cache Layer
Redis-backed caching for user preferences, fatigue scores, and feed lookups (<50ms).
"""

from typing import Any, Optional, Dict
from redis_client import get_cache, set_cache, delete_cache
from notification_platform.config import notification_config

_PREFIX_PREF = "notif:pref:"
_PREFIX_FATIGUE = "notif:fatigue:"


class NotificationCache:
    """Redis cache manager targeting <50ms lookup latency."""

    def get_preferences(self, user_id: int) -> Optional[Any]:
        if not notification_config.enable_redis_cache:
            return None
        return get_cache(f"{_PREFIX_PREF}{user_id}")

    def set_preferences(self, user_id: int, prefs: Any) -> bool:
        if not notification_config.enable_redis_cache:
            return False
        return set_cache(f"{_PREFIX_PREF}{user_id}", prefs, ttl=3600)

    def get_fatigue_score(self, user_id: int) -> Optional[float]:
        if not notification_config.enable_redis_cache:
            return None
        res = get_cache(f"{_PREFIX_FATIGUE}{user_id}")
        return float(res) if res is not None else None

    def set_fatigue_score(self, user_id: int, score: float) -> bool:
        if not notification_config.enable_redis_cache:
            return False
        return set_cache(f"{_PREFIX_FATIGUE}{user_id}", score, ttl=1800)


# Singleton
notification_cache = NotificationCache()
