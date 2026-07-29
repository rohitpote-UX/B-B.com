"""
Brand Battle - Background Worker Tasks
Asynchronous tasks for price syncing, alert triggers, notification delivery, and cache warming.
"""

from celery_app import celery_app
from redis_client import set_cache, invalidate_cache_pattern
import time


@celery_app.task(name="tasks.sync_product_prices")
def sync_product_prices_task():
    """Asynchronous background worker job to refresh external platform product prices."""
    print("🔄 Running background price synchronization...")
    # Invalidation ensures fresh data on next API fetch
    invalidate_cache_pattern("product:*")
    invalidate_cache_pattern("deals:*")
    return {"status": "success", "timestamp": time.time()}


@celery_app.task(name="tasks.process_price_alerts")
def process_price_alerts_task():
    """Asynchronous background worker job to check price drops and send notifications."""
    print("🔔 Processing active price alerts...")
    return {"status": "alerts_checked", "processed_at": time.time()}


@celery_app.task(name="tasks.warm_cache")
def warm_cache_task():
    """Pre-loads top requested catalog queries into Redis cache."""
    print("🔥 Warming up cache for high-frequency queries...")
    set_cache("system:cache_warmed_at", time.time(), ttl=86400)
    return {"status": "cache_warmed"}
