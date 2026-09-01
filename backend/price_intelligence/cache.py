"""
Brand Battle — Price Intelligence Redis Cache Layer
Redis-first caching for price reports, forecasts, trust scores, and fair market values.
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict

from redis_client import get_cache, set_cache, delete_cache, invalidate_cache_pattern, is_redis_healthy
from price_intelligence.config import price_intel_config

logger = logging.getLogger("brandbattle.price_intelligence.cache")

_PREFIX_REPORT = "price_intel:report:"
_PREFIX_FORECAST = "price_intel:forecast:"
_PREFIX_TRUST = "price_intel:trust:"
_PREFIX_FAIR_VALUE = "price_intel:fair_value:"


class PriceIntelligenceCache:
    """Redis-first cache manager targeting <50ms response latency."""

    def _hash_key(self, raw: str) -> str:
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]

    def get_report(self, product_id: int) -> Optional[Any]:
        if not price_intel_config.enable_redis_cache:
            return None
        return get_cache(f"{_PREFIX_REPORT}{product_id}")

    def set_report(self, product_id: int, report: Any) -> bool:
        if not price_intel_config.enable_redis_cache:
            return False
        return set_cache(
            f"{_PREFIX_REPORT}{product_id}",
            report,
            ttl=price_intel_config.cache_ttl.price_report_ttl,
        )

    def get_forecast(self, product_id: int) -> Optional[Any]:
        if not price_intel_config.enable_redis_cache:
            return None
        return get_cache(f"{_PREFIX_FORECAST}{product_id}")

    def set_forecast(self, product_id: int, forecast: Any) -> bool:
        if not price_intel_config.enable_redis_cache:
            return False
        return set_cache(
            f"{_PREFIX_FORECAST}{product_id}",
            forecast,
            ttl=price_intel_config.cache_ttl.forecast_ttl,
        )

    def invalidate_product_cache(self, product_id: int) -> int:
        """Invalidate caches for a product on price updates."""
        count = 0
        count += delete_cache(f"{_PREFIX_REPORT}{product_id}")
        count += delete_cache(f"{_PREFIX_FORECAST}{product_id}")
        count += delete_cache(f"{_PREFIX_FAIR_VALUE}{product_id}")
        return count


# Singleton
price_intel_cache = PriceIntelligenceCache()
