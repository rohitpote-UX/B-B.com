"""
Brand Battle — Admin Console Repository Layer
Database data access layer following the Repository Pattern for audit logs, review queue, and feature flags.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from admin_console.models import (
    AdminAuditLog, AdminReviewQueueItem, FeatureFlag, ExecutiveBriefRecord, AdminRolePermission
)


class AdminConsoleRepository:
    """Repository managing database access for the Admin Console Platform."""

    def log_action(
        self,
        db: Session,
        admin_user_id: int,
        admin_name: str,
        action_type: str,
        target_resource: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
    ) -> AdminAuditLog:
        """Log an immutable administrative audit action."""
        log = AdminAuditLog(
            admin_user_id=admin_user_id,
            admin_name=admin_name,
            action_type=action_type,
            target_resource=target_resource,
            before_state_json=before_state,
            after_state_json=after_state,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_recent_audit_logs(self, db: Session, limit: int = 20) -> List[AdminAuditLog]:
        """Fetch recent admin audit logs."""
        return (
            db.query(AdminAuditLog)
            .order_by(desc(AdminAuditLog.created_at))
            .limit(limit)
            .all()
        )

    def get_pending_review_queue(self, db: Session, limit: int = 30) -> List[AdminReviewQueueItem]:
        """Fetch active review queue items."""
        return (
            db.query(AdminReviewQueueItem)
            .filter(AdminReviewQueueItem.status == "pending")
            .order_by(desc(AdminReviewQueueItem.created_at))
            .limit(limit)
            .all()
        )

    def resolve_review_item(
        self, db: Session, item_id: int, action: str, notes: Optional[str] = None
    ) -> Optional[AdminReviewQueueItem]:
        """Resolve a review queue item."""
        item = db.query(AdminReviewQueueItem).filter(AdminReviewQueueItem.id == item_id).first()
        if item:
            item.status = "approved" if action == "approve" else "rejected"
            item.resolution_notes = notes
            item.resolved_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(item)
        return item

    def get_feature_flags(self, db: Session) -> List[FeatureFlag]:
        """Fetch all feature flags."""
        return db.query(FeatureFlag).order_by(asc(FeatureFlag.key)).all()

    def update_feature_flag(
        self, db: Session, key: str, is_enabled: bool, rollout_pct: float = 100.0
    ) -> Optional[FeatureFlag]:
        """Update or create a feature flag."""
        flag = db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
        if not flag:
            flag = FeatureFlag(key=key, name=key.replace("_", " ").title(), is_enabled=is_enabled, rollout_percentage=rollout_pct)
            db.add(flag)
        else:
            flag.is_enabled = is_enabled
            flag.rollout_percentage = rollout_pct
        db.commit()
        db.refresh(flag)
        return flag


# Singleton
admin_repo = AdminConsoleRepository()
