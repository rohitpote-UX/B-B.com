"""
Brand Battle — Enterprise Notification Platform Database Models
SQLAlchemy ORM models for notification events, preferences, history, digests, fatigue profiles, and feedback.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
)
from database import Base


class NotificationEvent(Base):
    """Raw triggered notification events."""
    __tablename__ = "notification_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # price_drop, buy_now, opportunity, wishlist, etc.
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    relevance_score = Column(Float, nullable=False, default=0.0)
    priority_level = Column(Integer, default=1)  # 1=Highest, 5=Lowest
    payload_json = Column(JSON, nullable=True)
    status = Column(String(20), default="pending", index=True)  # pending, delivered, suppressed, queued
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class NotificationPreference(Base):
    """User preference center settings."""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    enable_in_app = Column(Boolean, default=True)
    enable_email = Column(Boolean, default=True)
    enable_push = Column(Boolean, default=True)
    enable_daily_digest = Column(Boolean, default=True)
    digest_frequency = Column(String(20), default="daily")  # daily, weekly
    quiet_hours_start = Column(Integer, default=22)
    quiet_hours_end = Column(Integer, default=7)
    max_daily_notifications = Column(Integer, default=3)
    preferred_categories = Column(JSON, nullable=True)
    preferred_brands = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class NotificationHistory(Base):
    """Immutable audit log of delivered notifications."""
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    channel = Column(String(30), default="in_app")  # in_app, email, push, web
    relevance_score = Column(Float, default=0.0)
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    is_dismissed = Column(Boolean, default=False)
    delivered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class NotificationDigest(Base):
    """Stored Daily AI Digests."""
    __tablename__ = "notification_digests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    headline = Column(String(300), nullable=False)
    summary_text = Column(Text, nullable=False)
    deal_count = Column(Integer, default=0)
    total_savings_inr = Column(Float, default=0.0)
    items_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class FatigueProfile(Base):
    """Tracked user fatigue and responsiveness profiles."""
    __tablename__ = "fatigue_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    fatigue_score = Column(Float, default=0.0)  # 0-1.0
    dismissal_count_7d = Column(Integer, default=0)
    open_count_7d = Column(Integer, default=0)
    last_delivered_at = Column(DateTime, nullable=True)
    throttled_until = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NotificationFeedback(Base):
    """User feedback for Happiness Index calculation."""
    __tablename__ = "notification_feedback"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notification_history.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_helpful = Column(Boolean, nullable=False)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
