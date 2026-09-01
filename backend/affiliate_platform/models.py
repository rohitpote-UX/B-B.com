"""
Brand Battle — Affiliate Platform Database Models
SQLAlchemy ORM models for providers, deep links, clicks, conversions, campaigns, commissions, link health, and disclosures.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
)
from database import Base


class EnterpriseAffiliateProvider(Base):
    """Affiliate network provider registry (Amazon, Flipkart, Impact, CJ, Awin, Rakuten, Sovrn)."""
    __tablename__ = "affiliate_platform_providers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=1)
    base_commission_rate_pct = Column(Float, default=5.0)
    credentials_json = Column(JSON, nullable=True)
    health_status = Column(String(20), default="healthy")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EnterpriseAffiliateLink(Base):
    """Generated deep links mapping product & marketplace to affiliate URLs."""
    __tablename__ = "affiliate_platform_links"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    link_token = Column(String(100), unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    provider_key = Column(String(50), nullable=False, index=True)
    destination_url = Column(Text, nullable=False)
    affiliate_url = Column(Text, nullable=False)
    is_valid = Column(Boolean, default=True, index=True)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class EnterpriseAffiliateClick(Base):
    """Anonymized click logs for outbound affiliate traffic."""
    __tablename__ = "affiliate_platform_clicks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    click_id = Column(String(100), unique=True, nullable=False, index=True)
    link_id = Column(Integer, ForeignKey("affiliate_platform_links.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    provider_key = Column(String(50), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_type = Column(String(30), default="desktop")
    country = Column(String(10), default="IN")
    touchpoint = Column(String(50), default="search")
    is_suspicious_fraud = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class EnterpriseAffiliateConversion(Base):
    """Affiliate conversions & transaction records."""
    __tablename__ = "affiliate_platform_conversions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    conversion_id = Column(String(100), unique=True, nullable=False, index=True)
    provider_key = Column(String(50), nullable=False, index=True)
    order_id = Column(String(100), nullable=True)
    click_id = Column(String(100), nullable=True)
    sale_amount_inr = Column(Float, nullable=False)
    commission_amount_inr = Column(Float, nullable=False)
    status = Column(String(20), default="pending", index=True)
    converted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class EnterpriseAffiliateDisclosure(Base):
    """Transparent user disclosure notices."""
    __tablename__ = "affiliate_platform_disclosures"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    disclosure_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
