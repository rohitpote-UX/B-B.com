"""
Brand Battle - KG Cache Manager
Provides Knowledge Graph–aware cache key management and tag-based invalidation.
Wraps existing redis_client functions with KG-specific key patterns.
"""

from typing import Optional, Any
from redis_client import get_cache, set_cache, delete_cache, invalidate_cache_pattern
import logging

logger = logging.getLogger("brandbattle.kg.cache")

# KG-specific cache key patterns
KG_MASTER_KEY = "kg:master:{master_id}"
KG_OFFERS_KEY = "kg:offers:{master_id}"
KG_RELATIONSHIPS_KEY = "kg:relationships:{master_id}"
KG_STATS_KEY = "kg:stats"
KG_MASTER_LIST_KEY = "kg:masters:list:{page}:{page_size}"


class KGCacheManager:
    """Manages KG-specific cache keys with auto-invalidation on graph changes."""

    DEFAULT_TTL = 1800  # 30 minutes for KG data

    def get_master(self, master_id: int) -> Optional[dict]:
        """Get cached master product data."""
        key = KG_MASTER_KEY.format(master_id=master_id)
        return get_cache(key)

    def set_master(self, master_id: int, data: dict, ttl: int = None) -> bool:
        """Cache master product data."""
        key = KG_MASTER_KEY.format(master_id=master_id)
        return set_cache(key, data, ttl or self.DEFAULT_TTL)

    def get_offers(self, master_id: int) -> Optional[list]:
        """Get cached offers for a master product."""
        key = KG_OFFERS_KEY.format(master_id=master_id)
        return get_cache(key)

    def set_offers(self, master_id: int, data: list, ttl: int = None) -> bool:
        """Cache offers for a master product."""
        key = KG_OFFERS_KEY.format(master_id=master_id)
        return set_cache(key, data, ttl or self.DEFAULT_TTL)

    def get_relationships(self, master_id: int) -> Optional[list]:
        """Get cached relationships for a master product."""
        key = KG_RELATIONSHIPS_KEY.format(master_id=master_id)
        return get_cache(key)

    def set_relationships(self, master_id: int, data: list, ttl: int = None) -> bool:
        """Cache relationships for a master product."""
        key = KG_RELATIONSHIPS_KEY.format(master_id=master_id)
        return set_cache(key, data, ttl or self.DEFAULT_TTL)

    def get_stats(self) -> Optional[dict]:
        """Get cached KG stats."""
        return get_cache(KG_STATS_KEY)

    def set_stats(self, data: dict, ttl: int = 300) -> bool:
        """Cache KG stats (5 min TTL)."""
        return set_cache(KG_STATS_KEY, data, ttl)

    def invalidate_master(self, master_id: int) -> None:
        """Invalidate all cache entries for a specific master product."""
        delete_cache(KG_MASTER_KEY.format(master_id=master_id))
        delete_cache(KG_OFFERS_KEY.format(master_id=master_id))
        delete_cache(KG_RELATIONSHIPS_KEY.format(master_id=master_id))
        delete_cache(KG_STATS_KEY)
        # Also invalidate master list caches
        invalidate_cache_pattern("kg:masters:list:*")
        logger.debug(f"Invalidated KG cache for master {master_id}")

    def invalidate_all(self) -> None:
        """Invalidate all KG cache entries."""
        invalidate_cache_pattern("kg:*")
        logger.info("Invalidated all KG cache entries")
