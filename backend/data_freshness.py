"""
Brand Battle — Data Freshness Engine
Configuration-driven TTL management, freshness status computation,
and human-readable display labels for price/image verification timestamps.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("brandbattle.data_freshness")


# ─── Default TTL Constants (seconds) ─────────────────────────────────
# These serve as fallbacks if DataFreshnessConfig table is empty.

PRICE_TTL_HOT = 1800           # 30 minutes
PRICE_TTL_STANDARD = 21600     # 6 hours
PRICE_TTL_LOW_PRIORITY = 86400  # 24 hours
IMAGE_TTL = 86400              # 24 hours
ANOMALY_THRESHOLD_PCT = 40     # Price change % triggering anomaly flag

DEFAULT_CONFIG = {
    "PRICE_TTL_HOT": (PRICE_TTL_HOT, "Hot product price verification TTL (seconds)"),
    "PRICE_TTL_STANDARD": (PRICE_TTL_STANDARD, "Standard product price verification TTL (seconds)"),
    "PRICE_TTL_LOW_PRIORITY": (PRICE_TTL_LOW_PRIORITY, "Low-traffic product price verification TTL (seconds)"),
    "IMAGE_TTL": (IMAGE_TTL, "Image verification TTL (seconds)"),
    "ANOMALY_THRESHOLD_PCT": (ANOMALY_THRESHOLD_PCT, "Price change percentage threshold triggering anomaly flag"),
}


def get_freshness_config(db: Optional[Session] = None) -> Dict[str, int]:
    """
    Loads freshness TTL configuration from the database.
    Falls back to hardcoded defaults if DB is unavailable or config rows are missing.
    """
    config = {k: v[0] for k, v in DEFAULT_CONFIG.items()}

    if db is None:
        return config

    try:
        from models import DataFreshnessConfig
        rows = db.query(DataFreshnessConfig).all()
        for row in rows:
            config[row.config_key] = row.config_value
    except Exception as e:
        logger.warning(f"Could not load freshness config from DB: {e}")

    return config


def seed_freshness_config(db: Session) -> None:
    """Seeds default freshness configuration rows if they don't exist."""
    from models import DataFreshnessConfig

    for key, (value, description) in DEFAULT_CONFIG.items():
        existing = db.query(DataFreshnessConfig).filter(
            DataFreshnessConfig.config_key == key
        ).first()
        if not existing:
            db.add(DataFreshnessConfig(
                config_key=key,
                config_value=value,
                description=description
            ))

    db.commit()
    logger.info("✅ Data freshness config seeded")


# ─── Freshness Status Computation ─────────────────────────────────────

def determine_verification_status(
    verified_at: Optional[datetime],
    ttl_seconds: int = PRICE_TTL_STANDARD
) -> str:
    """
    Deterministic trust state computation based on elapsed time since last verification.

    Returns one of: 'verified', 'recently_verified', 'stale', 'unverified'

    Rules:
    - Within TTL: 'verified'
    - Within 2x TTL: 'recently_verified'
    - Beyond 2x TTL: 'stale'
    - No verification timestamp: 'unverified'
    """
    if verified_at is None:
        return "unverified"

    now = datetime.now(timezone.utc)
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)

    elapsed_seconds = (now - verified_at).total_seconds()

    if elapsed_seconds <= ttl_seconds:
        return "verified"
    elif elapsed_seconds <= ttl_seconds * 2:
        return "recently_verified"
    else:
        return "stale"


def get_freshness_display(verified_at: Optional[datetime]) -> str:
    """
    Returns a human-readable freshness label for UI display.

    Examples:
    - "Verified just now"
    - "Verified 4 min ago"
    - "Last checked 2 hours ago"
    - "Price may have changed"
    - "Not yet verified"
    """
    if verified_at is None:
        return "Not yet verified"

    now = datetime.now(timezone.utc)
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)

    elapsed = (now - verified_at).total_seconds()

    if elapsed < 60:
        return "Verified just now"
    elif elapsed < 3600:
        minutes = int(elapsed / 60)
        return f"Verified {minutes} min ago"
    elif elapsed < 86400:
        hours = int(elapsed / 3600)
        return f"Last checked {hours} hour{'s' if hours > 1 else ''} ago"
    elif elapsed < 604800:
        days = int(elapsed / 86400)
        return f"Last checked {days} day{'s' if days > 1 else ''} ago"
    else:
        return "Price may have changed"


def get_product_ttl_tier(
    view_count: int = 0,
    alert_count: int = 0,
    config: Optional[Dict[str, int]] = None
) -> int:
    """
    Determines the appropriate TTL tier for a product based on traffic and alerts.

    Priority logic:
    - P0/P1: Product has price alerts or >1000 views → HOT tier
    - P2/P3: Product has >100 views → STANDARD tier
    - P4/P5: Everything else → LOW_PRIORITY tier
    """
    if config is None:
        config = {k: v[0] for k, v in DEFAULT_CONFIG.items()}

    if alert_count > 0 or view_count > 1000:
        return config.get("PRICE_TTL_HOT", PRICE_TTL_HOT)
    elif view_count > 100:
        return config.get("PRICE_TTL_STANDARD", PRICE_TTL_STANDARD)
    else:
        return config.get("PRICE_TTL_LOW_PRIORITY", PRICE_TTL_LOW_PRIORITY)


def is_price_stale(
    verified_at: Optional[datetime],
    ttl_seconds: int = PRICE_TTL_STANDARD
) -> bool:
    """Returns True if the price needs re-verification based on its TTL tier."""
    if verified_at is None:
        return True

    now = datetime.now(timezone.utc)
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)

    return (now - verified_at).total_seconds() > ttl_seconds
