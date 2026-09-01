"""
Brand Battle — Analytics Platform Background Scheduler
Asynchronous background worker for periodic dashboard snapshotting, anomaly scanning, and continuous learning audits.
"""

import logging
from typing import Dict, Any
from database import SessionLocal
from analytics_platform.dashboard_service import executive_dashboard_service
from analytics_platform.anomaly_detection import anomaly_detection_engine

logger = logging.getLogger("brandbattle.analytics_platform.scheduler")


class AnalyticsScheduler:
    """Background task runner for analytics aggregations and governance checks."""

    def run_dashboard_snapshot_job(self) -> Dict[str, Any]:
        """Compute and cache executive dashboard snapshots."""
        db = SessionLocal()
        try:
            snapshot = executive_dashboard_service.get_dashboard_summary(db)
            anomalies = anomaly_detection_engine.scan_for_anomalies(db)
            logger.info(f"Analytics snapshot job completed: DAU={snapshot['dau']}, Anomalies={len(anomalies)}")
            return {"status": "success", "dau": snapshot["dau"], "anomalies_flagged": len(anomalies)}
        except Exception as e:
            logger.error(f"Analytics snapshot job failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()


# Singleton
analytics_scheduler = AnalyticsScheduler()
