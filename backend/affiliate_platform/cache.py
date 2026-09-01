"""
Brand Battle — Affiliate Platform Redis Cache Layer
Redis caching for generated deep links (<50ms target) and provider routing maps.
"""

from typing import Any, Optional, Dict
from redis_client import get_cache, set_cache

_PREFIX_DEEPLINK = "affiliate:deeplink:"


class AffiliateCache:
    """Redis cache manager for affiliate platform."""

    def get_deeplink(self, token: str) -> Optional[Any]:
        return get_cache(f"{_PREFIX_DEEPLINK}{token}")

    def set_deeplink(self, token: str, data: Any) -> bool:
        return set_cache(f"{_PREFIX_DEEPLINK}{token}", data, ttl=3600 * 24)


# Singleton
affiliate_cache = AffiliateCache()
