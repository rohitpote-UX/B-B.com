"""
Brand Battle — Catalog Engine Schemas
Data contracts for raw payloads, candidates, and job tracking.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class NormalizedProductCandidate(BaseModel):
    """Clean, structured intermediate representation of a product candidate."""
    raw_record_id: Optional[int] = None
    source_id: int
    source_name: str
    external_id: str
    source_url: Optional[str] = None
    
    # Core Identity
    brand: str
    canonical_brand: str
    raw_title: str
    clean_title: str
    canonical_name: str
    model_name: Optional[str] = None
    model_number: Optional[str] = None
    model_series: Optional[str] = None
    mpn: Optional[str] = None
    gtin: Optional[str] = None
    ean: Optional[str] = None
    upc: Optional[str] = None
    sku: Optional[str] = None
    is_gtin_valid: bool = False
    
    # Taxonomy
    raw_category: str
    canonical_category: str
    subcategory: Optional[str] = None
    product_type: Optional[str] = None
    
    # Variant Attributes
    variant_name: Optional[str] = None
    color: Optional[str] = None
    storage: Optional[str] = None
    ram: Optional[str] = None
    screen_size: Optional[str] = None
    variant_attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Content & Media
    description: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    primary_image_url: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    
    # Commercial / Marketplace Data (separate from product identity)
    has_offer: bool = False
    marketplace: Optional[str] = None
    seller_name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    currency: str = "INR"
    availability: bool = True
    stock_status: Optional[str] = "in_stock"
    affiliate_url: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    
    # Metadata & Quality
    quality_score: float = 0.0
    is_publishable: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class JobProgressResponse(BaseModel):
    """API response model for job monitoring."""
    job_id: int
    source_id: int
    source_name: str
    job_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cursor: Optional[str] = None
    records_seen: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_merged: int = 0
    records_reviewed: int = 0
    records_rejected: int = 0
    records_failed: int = 0
    error_summary: Optional[List[Dict[str, Any]]] = None


class CatalogSourceSchema(BaseModel):
    """Schema for CatalogSource configuration."""
    id: int
    name: str
    source_type: str
    base_url: Optional[str] = None
    adapter_key: str
    license_type: Optional[str] = None
    commercial_use_allowed: bool
    automated_access_allowed: bool
    requires_auth: bool
    active: bool
    priority: int
    terms_url: Optional[str] = None
    data_scope: Optional[str] = None
    last_sync_at: Optional[datetime] = None


class CatalogMetricsResponse(BaseModel):
    """Catalog health and ingestion performance dashboard metrics."""
    total_master_products: int
    total_variants: int
    total_brands: int
    total_categories: int
    total_marketplace_offers: int
    total_prices: int
    active_sources: int
    pending_review_count: int
    jobs_today: int
    records_processed_today: int
    records_created_today: int
    records_updated_today: int
    average_quality_score: float
    gtin_coverage_pct: float
    image_coverage_pct: float
