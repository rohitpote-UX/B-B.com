"""
Brand Battle — Verification Platform Pydantic Schemas
Defines request and response structures for PVTP endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SourceInfo(BaseModel):
    source_id: str
    name: str
    source_type: str  # official_cert, manufacturer, review_lab, retailer, community
    trust_score: float = Field(ge=0.0, le=100.0)
    country: str = "GLOBAL"
    update_frequency_hours: int = 24
    average_accuracy: float = 95.0
    historical_reliability: float = 95.0
    is_active: bool = True
    last_sync: Optional[datetime] = None


class SpecConfidence(BaseModel):
    spec_name: str
    claimed_value: Any
    verified_value: Any
    confidence_score: float = Field(ge=0.0, le=100.0)
    status: str = "Verified"  # Verified, Disputed, Unverified
    sources_count: int = 1
    evidence_hash: str
    last_verified: datetime


class TrustScoreResponse(BaseModel):
    product_id: int
    product_name: str
    trust_score: float = Field(ge=0.0, le=100.0)
    trust_tier: str  # Excellent, High, Moderate, Needs Review
    verification_percentage: float = Field(ge=0.0, le=100.0)
    sources_checked_count: int
    conflicts_resolved_count: int
    regional_variant: str = "Global / India"
    last_verified_at: datetime
    freshness_hours: float
    data_freshness_status: str  # Fresh, Moderate, Stale


class EvidenceReference(BaseModel):
    evidence_id: str
    spec_name: str
    source_id: str
    source_name: str
    raw_claim_value: Any
    evidence_hash: str
    verified_at: datetime
    trust_weight: float


class ConflictRecord(BaseModel):
    conflict_id: str
    spec_name: str
    disputed_values: Dict[str, Any]  # source_id -> claimed_value
    resolved_value: Any
    resolution_strategy: str
    confidence_score: float
    timestamp: datetime


class VerificationSummaryResponse(BaseModel):
    product_id: int
    product_name: str
    trust_score: TrustScoreResponse
    specifications_confidence: List[SpecConfidence]
    recent_conflicts: List[ConflictRecord]
    evidence_count: int
    sources_consulted: List[str]


class AuditLogRecord(BaseModel):
    audit_id: str
    product_id: int
    action: str
    actor: str
    details: Dict[str, Any]
    integrity_hash: str
    timestamp: datetime


class CommunitySuggestionRequest(BaseModel):
    product_id: int
    spec_name: str
    suggested_value: str
    evidence_url_or_text: str
    contributor_email: Optional[str] = None


class VerificationMetricsResponse(BaseModel):
    total_products_verified: int
    average_trust_score: float
    verification_success_rate: float
    active_sources_count: int
    conflicts_resolved_total: int
    pending_manual_reviews_count: int
    coverage_percentage: float
    stale_products_count: int
