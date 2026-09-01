"""
Brand Battle — Affiliate Platform Background Scheduler
Asynchronous background worker for periodic link validation and provider health monitoring.
"""

import logging
from typing import Dict, Any
from database import SessionLocal
from affiliate_platform.availability_checker import link_health_monitoring_engine

logger = logging.getLogger("brandbattle.affiliate_platform.scheduler")


class AffiliateScheduler:
    """Background task runner for affiliate link health monitoring."""

    def run_health_check_job(self) -> Dict[str, Any]:
        """Perform link health check job."""
        health = link_health_monitoring_engine.check_link_health()
        logger.info(f"Affiliate link health check completed: Healthy={health['healthy_links_pct']}%")
        return {"status": "success", "healthy_pct": health["healthy_links_pct"]}


# Singleton
affiliate_scheduler = AffiliateScheduler()
