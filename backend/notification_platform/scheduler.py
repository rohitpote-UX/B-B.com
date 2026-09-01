"""
Brand Battle — Notification Platform Background Scheduler
Asynchronous background worker for periodic Daily Digest generation and quiet hours dispatching.
"""

import logging
from typing import Dict, Any
from database import SessionLocal
from models import User
from notification_platform.digest_generator import digest_generator

logger = logging.getLogger("brandbattle.notification_platform.scheduler")


class NotificationScheduler:
    """Background task runner for periodic digests and delayed notifications."""

    def run_daily_digest_job(self) -> Dict[str, Any]:
        """Generate Daily AI Digests for active users."""
        db = SessionLocal()
        generated = 0
        try:
            users = db.query(User).filter(User.is_active == True).limit(100).all()
            for u in users:
                digest_generator.generate_digest(db, u)
                generated += 1
            logger.info(f"Daily Digest job completed: {generated} digests created")
            return {"status": "success", "digests_generated": generated}
        except Exception as e:
            logger.error(f"Daily Digest job failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()


# Singleton
notification_scheduler = NotificationScheduler()
