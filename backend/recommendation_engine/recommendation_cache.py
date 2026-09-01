"""
Brand Battle — Recommendation Cache Manager
High-performance Redis-first caching strategy with event-driven cache invalidation.
"""

from typing import Any, Optional, Dict
import json
from redis_client import is_redis_healthy, get_cache, set_cache, delete_cache
from recommendation_engine.recommendation_config import recommendation_settings
from logging_config import logger


class RecommendationCache:
    """Redis-first cache manager for storing and invalidating recommendation payloads."""

    def __init__(self):
        self.ttl_config = recommendation_settings.cache_ttl

    def _build_key(self, prefix: str, identifier: str) -> str:
        """Construct namespaced Redis key."""
        return f"bb:recommendations:{prefix}:{identifier}"

    def get_cached_recommendation(self, prefix: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieve recommendation payload from Redis cache."""
        if not recommendation_settings.enable_redis_cache:
            return None

        key = self._build_key(prefix, identifier)
        data = get_cache(key)
        if data:
            try:
                logger.debug(f"⚡ Recommendation cache HIT: {key}")
                return data if isinstance(data, dict) else json.loads(data)
            except Exception as e:
                logger.error(f"Failed to parse cached JSON for {key}: {e}")
        return None

    def set_cached_recommendation(
        self, 
        prefix: str, 
        identifier: str, 
        payload: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """Store recommendation payload into Redis cache."""
        if not recommendation_settings.enable_redis_cache:
            return False

        key = self._build_key(prefix, identifier)
        expire_time = ttl or self.ttl_config.product_recommendation_ttl
        try:
            return set_cache(key, payload, ttl=expire_time)
        except Exception as e:
            logger.error(f"Failed to cache recommendation for {key}: {e}")
            return False

    def invalidate_product_recommendations(self, product_id: int):
        """Invalidate all recommendation keys associated with a product."""
        key = self._build_key("product", str(product_id))
        delete_cache(key)
        logger.info(f"🗑️ Invalidated recommendation cache for product {product_id}")
