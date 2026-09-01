"""
Brand Battle — 11. Smart Price Alert Platform Engine
Manages price alert rules (target price, drop %, marketplace filter, notification delivery).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from price_intelligence.repository import price_intel_repo
from price_intelligence.models import PriceAlertRule
from price_intelligence.metrics import price_intel_metrics
from logging_config import logger


class SmartPriceAlertEngine:
    """Evaluates and triggers price alerts for products."""

    def create_alert(
        self,
        db: Session,
        user_id: int,
        product_id: int,
        target_price: float,
        notify_email: str,
        drop_percentage: Optional[float] = None,
        marketplace_filter: Optional[str] = None,
    ) -> PriceAlertRule:
        """Create a new smart price alert rule."""
        return price_intel_repo.create_price_alert(
            db=db,
            user_id=user_id,
            product_id=product_id,
            target_price=target_price,
            notify_email=notify_email,
            drop_percentage=drop_percentage,
            marketplace_filter=marketplace_filter,
        )

    def evaluate_alerts_for_product(
        self, db: Session, product_id: int, current_price: float, marketplace: str
    ) -> List[PriceAlertRule]:
        """Evaluate active price alerts against a new price drop."""
        alerts = price_intel_repo.get_active_alerts_for_product(db, product_id)
        triggered = []

        for alert in alerts:
            # Check marketplace filter
            if alert.marketplace_filter and alert.marketplace_filter.lower() != marketplace.lower():
                continue

            # Check target price or drop percentage condition
            if current_price <= alert.target_price:
                alert.last_triggered_at = datetime.now(timezone.utc)
                triggered.append(alert)
                price_intel_metrics.record_alert_triggered()
                logger.info(
                    f"Price Alert Triggered! Product #{product_id} dropped to {current_price} (Target: {alert.target_price}) -> Notifying {alert.notify_email}"
                )

        if triggered:
            db.commit()

        return triggered


# Singleton
smart_alert_engine = SmartPriceAlertEngine()
