"""
Brand Battle — Admin Console Background Scheduler
Asynchronous background worker for morning brief pre-generation and review queue SLA monitoring.
"""

import logging
from typing import Dict, Any
from database import SessionLocal
from admin_console.executive_brief import executive_brief_engine

logger = logging.getLogger("brandbattle.admin_console.scheduler")


class AdminConsoleScheduler:
    """Background task runner for Executive Morning Brief generation and SLA tracking."""

    def run_morning_brief_job(self) -> Dict[str, Any]:
        """Pre-generate Executive Morning Brief."""
        db = SessionLocal()
        try:
            brief = executive_brief_engine.generate_morning_brief(db)
            logger.info(f"Executive Morning Brief job completed for {brief.date_str}")
            return {"status": "success", "date": brief.date_str}
        except Exception as e:
            logger.error(f"Executive Morning Brief job failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()


# Singleton
admin_scheduler = AdminConsoleScheduler()
