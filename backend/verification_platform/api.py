"""
Brand Battle — Verification Platform API Router
Exposes read-only & management endpoints for PVTP.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from verification_platform.schemas import (
    VerificationSummaryResponse,
    TrustScoreResponse,
    SourceInfo,
    VerificationMetricsResponse,
    CommunitySuggestionRequest,
    AuditLogRecord
)
from verification_platform.services import verification_service

router = APIRouter(prefix="/api/verification", tags=["Product Verification Platform"])


@router.get("/summary/{product_id}", response_model=VerificationSummaryResponse)
async def get_verification_summary(
    product_id: int = Path(..., description="ID of product to fetch verification summary for")
):
    """Returns complete verification summary, spec confidence scores, evidence count, and conflicts."""
    try:
        return verification_service.get_verification_summary(product_id=product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate verification summary: {str(e)}")


@router.get("/trust-score/{product_id}", response_model=TrustScoreResponse)
async def get_product_trust_score(
    product_id: int = Path(..., description="ID of product to fetch Trust Score for")
):
    """Returns public Trust Score card metrics (% score, tier, sources checked, freshness)."""
    summary = verification_service.get_verification_summary(product_id=product_id)
    return summary.trust_score


@router.get("/sources", response_model=List[SourceInfo])
async def list_sources():
    """Lists all registered official and third-party data sources with dynamic trust scores."""
    return verification_service.get_sources()


@router.get("/metrics", response_model=VerificationMetricsResponse)
async def get_verification_metrics():
    """Returns platform-wide verification coverage, average trust score, and conflict health statistics."""
    return verification_service.get_metrics()


@router.get("/audit-trail", response_model=List[AuditLogRecord])
async def get_audit_trail(
    product_id: Optional[int] = Query(None, description="Optional product ID filter")
):
    """Returns immutable cryptographic audit log records for verification actions."""
    return verification_service.get_audit_logs(product_id=product_id)


@router.post("/community-suggest")
async def submit_community_suggestion(req: CommunitySuggestionRequest):
    """Allows knowledgeable users to submit specification corrections backed by evidence."""
    return verification_service.submit_community_suggestion(req)


@router.post("/verify/{product_id}", response_model=VerificationSummaryResponse)
async def trigger_immediate_verification(
    product_id: int = Path(..., description="Product ID to trigger verification cycle for")
):
    """Triggers an immediate automated 12-stage re-verification run for a product."""
    return verification_service.get_verification_summary(product_id=product_id)
