"""
Brand Battle — Admin Console Database Models
SQLAlchemy ORM models for audit logs, review queue, feature flags, morning briefs, and RBAC permissions.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
)
from database import Base


class AdminAuditLog(Base):
    """Immutable audit log trail of all administrative actions and AI overrides."""
    __tablename__ = "admin_audit_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    admin_name = Column(String(150), nullable=False)
    action_type = Column(String(100), nullable=False, index=True)  # product_override, matching_approval, flag_toggled
    target_resource = Column(String(150), nullable=False)
    before_state_json = Column(JSON, nullable=True)
    after_state_json = Column(JSON, nullable=True)
    ip_address = Column(String(45), default="127.0.0.1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class AdminReviewQueueItem(Base):
    """Unified Review Queue item for product merges, matching reviews, and content moderation."""
    __tablename__ = "admin_review_queue_items"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String(50), nullable=False, index=True)  # matching_review, product_merge, content_moderation
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium", index=True)  # low, medium, high, critical
    confidence_score = Column(Float, nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="pending", index=True)   # pending, approved, rejected, resolved
    resolution_notes = Column(Text, nullable=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime, nullable=True)


class FeatureFlag(Base):
    """Feature flag definitions and percentage rollout configurations."""
    __tablename__ = "admin_feature_flags"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=False, index=True)
    rollout_percentage = Column(Float, default=100.0)  # 0-100%
    subsystem = Column(String(50), default="general")  # search, rec, price, notification, UI
    rules_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExecutiveBriefRecord(Base):
    """Cached Executive Morning Brief snapshots."""
    __tablename__ = "admin_executive_briefs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    narrative_summary = Column(Text, nullable=False)
    metrics_summary_json = Column(JSON, nullable=False)
    date_str = Column(String(20), unique=True, nullable=False, index=True)  # YYYY-MM-DD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AdminRolePermission(Base):
    """Granular RBAC role permission mapping."""
    __tablename__ = "admin_role_permissions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), nullable=False, index=True)
    permission_key = Column(String(100), nullable=False)
    is_allowed = Column(Boolean, default=True)
