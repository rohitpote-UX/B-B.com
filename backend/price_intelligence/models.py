"""
Brand Battle — Enterprise Price Intelligence Database Models
SQLAlchemy ORM models for historical price snapshots, alert rules, trust scores, opportunity records, and audit logs.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, UniqueConstraint
)
from database import Base


class PriceSnapshot(Base):
    """Immutable historical price records tracked over time."""
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=True, index=True)
    marketplace = Column(String(50), nullable=False, index=True)
    seller_name = Column(String(100), nullable=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    shipping_cost = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    coupon_discount = Column(Float, default=0.0)
    effective_final_price = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("idx_snapshot_product_time", "product_id", "created_at"),
        Index("idx_snapshot_marketplace_time", "marketplace", "created_at"),
    )


class PriceAlertRule(Base):
    """User-defined price alert rules."""
    __tablename__ = "price_alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    drop_percentage = Column(Float, nullable=True)
    marketplace_filter = Column(String(50), nullable=True)
    notify_email = Column(String(150), nullable=False)
    notify_sms = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class MarketplaceTrustScore(Base):
    """Marketplace & seller reliability trust records."""
    __tablename__ = "marketplace_trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    marketplace = Column(String(50), unique=True, nullable=False, index=True)
    trust_score = Column(Float, nullable=False, default=85.0)  # 0-100
    delivery_speed_score = Column(Float, default=85.0)
    refund_success_score = Column(Float, default=90.0)
    seller_reliability_score = Column(Float, default=85.0)
    inventory_accuracy_score = Column(Float, default=90.0)
    price_stability_score = Column(Float, default=80.0)
    warranty_quality_score = Column(Float, default=85.0)
    customer_satisfaction_score = Column(Float, default=88.0)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class OpportunityScoreRecord(Base):
    """Audit log of calculated Brand Battle Opportunity Scores."""
    __tablename__ = "opportunity_score_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    opportunity_score = Column(Float, nullable=False)  # 0-100
    buy_confidence_score = Column(Float, nullable=False)
    buy_recommendation = Column(String(50), nullable=False)
    fair_market_value = Column(Float, nullable=False)
    fake_discount_detected = Column(Boolean, default=False)
    fake_discount_pct = Column(Float, default=0.0)
    market_heat_status = Column(String(50), default="🟢 Best Time to Buy")
    signals_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DiscountAuditRecord(Base):
    """Audit log of fake discount detection checks."""
    __tablename__ = "discount_audit_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    claimed_mrp = Column(Float, nullable=False)
    historical_avg_mrp = Column(Float, nullable=False)
    current_selling_price = Column(Float, nullable=False)
    claimed_discount_pct = Column(Float, nullable=False)
    real_discount_pct = Column(Float, nullable=False)
    fake_discount_pct = Column(Float, default=0.0)
    is_manipulated = Column(Boolean, default=False)
    trust_score = Column(Float, default=100.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
