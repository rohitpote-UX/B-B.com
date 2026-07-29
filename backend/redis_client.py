"""
Brand Battle - Redis Caching & Rate Limiting Client
Provides high-performance TTL caching, auto-invalidation, and Redis connection fallback.
"""

import json
from typing import Any, Optional
from config import settings

try:
    import redis
    redis_available = True
except ImportError:
    redis = None
    redis_available = False

# Global Redis client instance
redis_client: Any = None

try:
    if redis_available and settings.REDIS_ENABLED and settings.REDIS_URL:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
        # Test connection
        redis_client.ping()
        print("✅ Redis connected successfully")
except Exception as e:
    print(f"⚠️ Redis connection disabled or unreachable ({e}). Operating in cache-bypass mode.")
    redis_client = None


def is_redis_healthy() -> bool:
    """Check if Redis connection is active and healthy."""
    if redis_client is None:
        return False
    try:
        return redis_client.ping()
    except Exception:
        return False


def get_cache(key: str) -> Optional[Any]:
    """Retrieve and deserialize cached JSON value by key."""
    if not is_redis_healthy():
        return None
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        print(f"⚠️ Redis get error for key '{key}': {e}")
    return None


def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Serialize and cache JSON value with expiration TTL (seconds)."""
    if not is_redis_healthy():
        return False
    try:
        ttl_seconds = ttl if ttl is not None else settings.REDIS_CACHE_TTL
        serialized = json.dumps(value, default=str)
        return bool(redis_client.setex(key, ttl_seconds, serialized))
    except Exception as e:
        print(f"⚠️ Redis set error for key '{key}': {e}")
        return False


def delete_cache(key: str) -> bool:
    """Delete explicit cache key."""
    if not is_redis_healthy():
        return False
    try:
        return bool(redis_client.delete(key))
    except Exception as e:
        print(f"⚠️ Redis delete error for key '{key}': {e}")
        return False


def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate all keys matching pattern (e.g. 'product:*', 'deals:*')."""
    if not is_redis_healthy():
        return 0
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
    except Exception as e:
        print(f"⚠️ Redis pattern invalidation error for '{pattern}': {e}")
    return 0
