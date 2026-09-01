"""
Brand Battle — Enterprise Analytics Platform Database Models
SQLAlchemy ORM models for events, sessions, journeys, funnels, metrics, cohorts, insights, experiments, and anomalies.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
)
from database import Base


class AnalyticsEvent(Base):
    """Immutable universal analytics log for all platform events."""
    __tablename__ = "platform_analytics_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    correlation_id = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    device_type = Column(String(30), default="desktop")
    browser = Column(String(50), default="chrome")
    country = Column(String(10), default="IN")
    currency = Column(String(10), default="INR")
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class UserSession(Base):
    """User browsing session records."""
    __tablename__ = "analytics_user_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    device_type = Column(String(30), default="desktop")
    entry_page = Column(String(250), nullable=True)
    event_count = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    ended_at = Column(DateTime, nullable=True)


class UserJourney(Base):
    """User decision journey stage tracking."""
    __tablename__ = "analytics_user_journeys"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    current_stage = Column(String(50), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    converted_to_intent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FunnelDefinition(Base):
    """Custom conversion funnel definitions."""
    __tablename__ = "analytics_funnel_definitions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    steps_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InsightReport(Base):
    """Generated AI Plain-Language Decision Insights."""
    __tablename__ = "analytics_insight_reports"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    category = Column(String(50), nullable=False)
    narrative_text = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.90)
    impact_level = Column(String(20), default="high")
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class AnomalyRecord(Base):
    """Detected operational & metric anomaly alerts."""
    __tablename__ = "analytics_anomaly_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    anomaly_type = Column(String(100), nullable=False)
    subsystem = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="warning")
    metric_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DashboardSnapshot(Base):
    """Cached executive dashboard snapshots."""
    __tablename__ = "analytics_dashboard_snapshots"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    dau = Column(Integer, default=0)
    mau = Column(Integer, default=0)
    retention_rate_pct = Column(Float, default=0.0)
    rec_ctr_pct = Column(Float, default=0.0)
    search_success_pct = Column(Float, default=0.0)
    price_forecast_accuracy_pct = Column(Float, default=0.0)
    notification_happiness_pct = Column(Float, default=0.0)
    snapshot_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
