"""
Brand Battle — Search Cache Manager
Redis-first caching strategy for queries, autocomplete, facets, and popular queries.
Gracefully bypasses when Redis is unavailable.
"""

import json
import hashlib
import logging
from typing import Any, Optional, Dict

from redis_client import get_cache, set_cache, delete_cache, invalidate_cache_pattern, is_redis_healthy
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.cache")

# Cache key prefixes
_PREFIX_QUERY = "search:query:"
_PREFIX_AUTOCOMPLETE = "search:autocomplete:"
_PREFIX_FACET = "search:facet:"
_PREFIX_POPULAR = "search:popular:"
_PREFIX_TRENDING = "search:trending:"
_PREFIX_SUGGESTION = "search:suggestion:"


class SearchCache:
    """Redis-first search result caching with event-driven invalidation."""

    def _hash_key(self, raw: str) -> str:
        """Generate a short deterministic hash for cache keys."""
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]

    # ─── Query Result Cache ──────────────────────────────────────────

    def get_query_result(self, query: str, filters: Optional[Dict] = None) -> Optional[Any]:
        """Retrieve cached search results for a query + filter combination."""
        if not search_config.enable_redis_cache:
            return None
        key = _PREFIX_QUERY + self._hash_key(f"{query}|{json.dumps(filters or {}, sort_keys=True)}")
        return get_cache(key)

    def set_query_result(self, query: str, filters: Optional[Dict], result: Any) -> bool:
        """Cache search results."""
        if not search_config.enable_redis_cache:
            return False
        key = _PREFIX_QUERY + self._hash_key(f"{query}|{json.dumps(filters or {}, sort_keys=True)}")
        return set_cache(key, result, ttl=search_config.cache_ttl.query_result_ttl)

    # ─── Facet Cache ─────────────────────────────────────────────────

    def get_facet_cache(self, query: str) -> Optional[Any]:
        if not search_config.enable_redis_cache:
            return None
        key = _PREFIX_FACET + self._hash_key(query)
        return get_cache(key)

    def set_facet_cache(self, query: str, facets: Any) -> bool:
        if not search_config.enable_redis_cache:
            return False
        key = _PREFIX_FACET + self._hash_key(query)
        return set_cache(key, facets, ttl=search_config.cache_ttl.facet_ttl)

    # ─── Popular / Trending Cache ────────────────────────────────────

    def get_popular_queries(self) -> Optional[Any]:
        if not search_config.enable_redis_cache:
            return None
        return get_cache(_PREFIX_POPULAR + "top")

    def set_popular_queries(self, queries: Any) -> bool:
        if not search_config.enable_redis_cache:
            return False
        return set_cache(_PREFIX_POPULAR + "top", queries, ttl=search_config.cache_ttl.popular_query_ttl)

    def get_trending_searches(self) -> Optional[Any]:
        if not search_config.enable_redis_cache:
            return None
        return get_cache(_PREFIX_TRENDING + "top")

    def set_trending_searches(self, searches: Any) -> bool:
        if not search_config.enable_redis_cache:
            return False
        return set_cache(_PREFIX_TRENDING + "top", searches, ttl=search_config.cache_ttl.trending_ttl)

    # ─── Invalidation ────────────────────────────────────────────────

    def invalidate_all_search(self) -> int:
        """Invalidate all search-related caches."""
        count = 0
        count += invalidate_cache_pattern("search:query:*")
        count += invalidate_cache_pattern("search:facet:*")
        count += invalidate_cache_pattern("search:autocomplete:*")
        count += invalidate_cache_pattern("search:popular:*")
        count += invalidate_cache_pattern("search:trending:*")
        count += invalidate_cache_pattern("search:suggestion:*")
        logger.info(f"Invalidated {count} search cache keys")
        return count

    def invalidate_query_cache(self) -> int:
        """Invalidate query result caches only."""
        return invalidate_cache_pattern("search:query:*")

    def invalidate_autocomplete_cache(self) -> int:
        """Invalidate autocomplete suggestion caches."""
        return invalidate_cache_pattern("search:autocomplete:*")


# Singleton
search_cache = SearchCache()
