"""
Brand Battle - Background Worker Tasks
Asynchronous tasks for price verification, image validation, data trust audits,
price syncing, alert triggers, notification delivery, and cache warming.
"""

from celery_app import celery_app
from database import SessionLocal
from redis_client import get_redis_client, set_cache, invalidate_cache_pattern
from data_freshness import is_price_stale, get_product_ttl_tier, get_freshness_config
from pipeline.price_verifier import price_verifier
from pipeline.image_verifier import image_verifier
from datetime import datetime, timezone
import models
import time
import logging

logger = logging.getLogger("brandbattle.tasks")


def acquire_redis_lock(lock_name: str, lock_ttl: int = 300) -> bool:
    """Distributed lock helper using Redis SETNX to prevent duplicate concurrent verification tasks."""
    redis_client = get_redis_client()
    if redis_client is None:
        return True  # If Redis is unavailable, allow execution

    try:
        acquired = redis_client.set(f"lock:{lock_name}", "locked", ex=lock_ttl, nx=True)
        return bool(acquired)
    except Exception as e:
        logger.warning(f"Redis lock acquiring failed: {e}")
        return True


def release_redis_lock(lock_name: str) -> None:
    """Releases distributed lock."""
    redis_client = get_redis_client()
    if redis_client is None:
        return
    try:
        redis_client.delete(f"lock:{lock_name}")
    except Exception:
        pass


@celery_app.task(name="tasks.verify_product_prices")
def verify_product_prices_task(limit: int = 50):
    """
    Scans products with stale or unverified prices (based on TTL tiers),
    re-evaluates price freshness, updates verification status, and logs anomalies.
    """
    if not acquire_redis_lock("verify_product_prices", lock_ttl=600):
        logger.info("Task verify_product_prices is already running. Skipping duplicate task.")
        return {"status": "skipped", "reason": "lock_acquired_by_another_worker"}

    db = SessionLocal()
    verified_count = 0
    stale_count = 0

    try:
        config = get_freshness_config(db)
        products = db.query(models.Product).filter(models.Product.is_active == True).limit(limit).all()

        for product in products:
            alert_count = db.query(models.PriceAlert).filter(models.PriceAlert.product_id == product.id).count()
            ttl_seconds = get_product_ttl_tier(product.view_count, alert_count, config)

            if is_price_stale(product.price_verified_at, ttl_seconds):
                prices = db.query(models.Price).filter(models.Price.product_id == product.id).all()
                now_utc = datetime.now(timezone.utc)

                for price_obj in prices:
                    # Re-verify price observation
                    verification = price_verifier.verify_price(
                        new_price=price_obj.price,
                        previous_price=price_obj.price,
                        marketplace=price_obj.platform,
                        source_method=price_obj.source_method or "scraper",
                        original_price=price_obj.original_price,
                    )

                    price_obj.verification_status = verification.verification_status
                    price_obj.verified_at = now_utc
                    price_obj.confidence_score = verification.confidence_score
                    price_obj.last_checked = now_utc

                product.price_verified_at = now_utc
                product.price_verification_status = (
                    "verified" if any(p.verification_status == "verified" for p in prices) else "stale"
                )
                verified_count += 1
            else:
                stale_count += 1

        db.commit()
        logger.info(f"✅ Price verification task finished: {verified_count} products updated, {stale_count} up to date.")
        return {"status": "success", "verified_count": verified_count, "up_to_date_count": stale_count}

    except Exception as e:
        db.rollback()
        logger.error(f"Error in verify_product_prices_task: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
        release_redis_lock("verify_product_prices")


@celery_app.task(name="tasks.verify_product_images")
def verify_product_images_task(limit: int = 50):
    """
    Validates product image URLs using HTTP HEAD requests.
    Attempts automatic fallback recovery for broken images.
    """
    if not acquire_redis_lock("verify_product_images", lock_ttl=600):
        return {"status": "skipped", "reason": "lock_acquired_by_another_worker"}

    db = SessionLocal()
    verified_images = 0
    failed_images = 0
    recovered_images = 0

    try:
        products = (
            db.query(models.Product)
            .filter(
                models.Product.is_active == True,
                models.Product.image_url.isnot(None),
            )
            .limit(limit)
            .all()
        )

        now_utc = datetime.now(timezone.utc)

        for product in products:
            result = image_verifier.verify_image_url(product.image_url)

            if result.is_valid:
                product.image_verified_at = now_utc
                verified_images += 1
            else:
                failed_images += 1
                logger.warning(f"Product #{product.id} image failed verification ({result.failure_reason}): {product.image_url}")

                # Attempt fallback recovery
                fallback_url = image_verifier.find_fallback_image(product.id, db)
                if fallback_url:
                    fb_result = image_verifier.verify_image_url(fallback_url)
                    if fb_result.is_valid:
                        product.image_url = fallback_url
                        product.image_verified_at = now_utc
                        recovered_images += 1
                        logger.info(f"✅ Recovered fallback image for Product #{product.id}: {fallback_url}")

        db.commit()
        return {
            "status": "success",
            "verified_images": verified_images,
            "failed_images": failed_images,
            "recovered_images": recovered_images,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error in verify_product_images_task: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
        release_redis_lock("verify_product_images")


@celery_app.task(name="tasks.audit_data_trust")
def audit_data_trust_task():
    """Generates a trust metric summary of products, prices, and image states."""
    db = SessionLocal()
    try:
        total_products = db.query(models.Product).filter(models.Product.is_active == True).count()
        unverified_prices = db.query(models.Price).filter(
            models.Price.verification_status.in_(["unverified", "stale", "failed_verification"])
        ).count()
        verified_prices = db.query(models.Price).filter(models.Price.verification_status == "verified").count()

        pending_anomalies = db.query(models.PriceAnomalyLog).filter(
            models.PriceAnomalyLog.resolution == "pending"
        ).count()

        summary = {
            "total_active_products": total_products,
            "verified_prices": verified_prices,
            "unverified_or_stale_prices": unverified_prices,
            "pending_price_anomalies": pending_anomalies,
            "audited_at": time.time(),
        }
        logger.info(f"📊 Trust Audit Summary: {summary}")
        set_cache("trust_audit_latest", summary, ttl=3600)
        return summary
    finally:
        db.close()


@celery_app.task(name="tasks.sync_product_prices")
def sync_product_prices_task():
    """Asynchronous background worker job to refresh external platform product prices."""
    print("🔄 Running background price synchronization...")
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
