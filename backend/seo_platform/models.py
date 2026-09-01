"""
Brand Battle — SEO Platform Database Models
SQLAlchemy ORM models for cached metadata records and sitemap generation logs.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
)
from database import Base


class SeoMetadataRecord(Base):
    """Cached SEO metadata and canonical mapping for comparison pages."""
    __tablename__ = "seo_metadata_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    canonical_slug = Column(String(250), unique=True, nullable=False, index=True)
    product1_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product2_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    title = Column(String(250), nullable=False)
    meta_description = Column(Text, nullable=False)
    canonical_url = Column(String(500), nullable=False)
    open_graph_json = Column(JSON, nullable=True)
    json_ld_schema_json = Column(JSON, nullable=True)
    validation_status = Column(String(20), default="valid", index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)


class SitemapIndexRecord(Base):
    """Sitemap tracking records."""
    __tablename__ = "seo_sitemap_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    sitemap_type = Column(String(50), nullable=False, index=True)  # comparison, product, category, brand
    url_count = Column(Integer, default=0)
    xml_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
