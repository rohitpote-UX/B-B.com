"""
Brand Battle — Price Intelligence Background Scheduler
Asynchronous background worker for periodic price alert evaluation and forecast recalculation.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from database import SessionLocal

from price_intelligence.alert_engine import smart_alert_engine
from price_intelligence.cache import price_intel_cache
from models import Product

logger = logging.getLogger("brandbattle.price_intelligence.scheduler")


class PriceIntelligenceScheduler:
    """Background task runner for price alert checks and cache refreshes."""

    def run_scheduled_alert_check(self) -> Dict[str, Any]:
        """Scan active products and evaluate price alert rules."""
        db = SessionLocal()
        triggered_count = 0
        try:
            products = db.query(Product).filter(Product.is_active == True).limit(200).all()
            for p in products:
                current_price = p.current_best_price or 0.0
                mp = p.current_best_platform or "amazon"
                if current_price > 0:
                    alerts = smart_alert_engine.evaluate_alerts_for_product(
                        db, p.id, current_price, mp
                    )
                    triggered_count += len(alerts)

            logger.info(f"Scheduled alert check complete: {triggered_count} alerts triggered")
            return {"status": "success", "alerts_triggered": triggered_count}
        except Exception as e:
            logger.error(f"Scheduled alert check failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()


# Singleton
price_intel_scheduler = PriceIntelligenceScheduler()
