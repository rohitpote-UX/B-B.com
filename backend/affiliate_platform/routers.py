"""
Brand Battle — Enterprise Affiliate Platform REST API Layer
FastAPI router mounted at /api/affiliate/* providing deep link generation, click redirection, conversions, and commission dashboards.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from affiliate_platform.services import affiliate_platform_service
from affiliate_platform.click_tracker import click_tracker_engine
from affiliate_platform.conversion_tracker import conversion_tracker_engine
from affiliate_platform.provider_registry import provider_registry
from affiliate_platform.metrics import affiliate_metrics
from affiliate_platform.repository import affiliate_repo
from affiliate_platform.schemas import (
    DeepLinkRequestSchema, ClickLogRequestSchema, ConversionLogRequestSchema
)

router = APIRouter(prefix="/api/affiliate", tags=["Affiliate Commerce Platform"])


@router.post("/deeplink")
async def generate_deeplink(
    payload: DeepLinkRequestSchema,
    db: Session = Depends(get_db),
):
    """Generate product affiliate deep link targeting <50ms latency."""
    res = affiliate_platform_service.generate_product_deeplink(
        db=db,
        product_id=payload.product_id,
        destination_url=payload.destination_url,
        marketplace_name=payload.marketplace_name or "Amazon",
        touchpoint=payload.touchpoint or "search",
        session_id=payload.session_id or "guest_session",
    )
    return {
        "success": True,
        "message": "Affiliate deep link generated",
        "data": res.model_dump(),
    }


@router.get("/redirect/{link_token}")
async def redirect_affiliate(
    link_token: str,
    db: Session = Depends(get_db),
):
    """Perform non-blocking click tracking and redirect to retailer destination URL."""
    link = affiliate_repo.get_link_by_token(db, link_token)
    if not link:
        raise HTTPException(status_code=404, detail="Affiliate link not found")

    click_tracker_engine.track_click(
        db=db,
        link_token=link_token,
        product_id=link.product_id,
        provider_key=link.provider_key,
    )
    affiliate_metrics.record_click()

    return RedirectResponse(url=link.affiliate_url, status_code=302)


@router.post("/click")
async def log_click(
    payload: ClickLogRequestSchema,
    db: Session = Depends(get_db),
):
    """Async click logging endpoint."""
    link = affiliate_repo.get_link_by_token(db, payload.link_token)
    pid = link.product_id if link else 1
    pkey = link.provider_key if link else "amazon"

    res = click_tracker_engine.track_click(
        db=db,
        link_token=payload.link_token,
        product_id=pid,
        provider_key=pkey,
        session_id=payload.session_id or "guest_session",
        touchpoint=payload.touchpoint or "search",
    )
    return {
        "success": True,
        "message": "Click logged successfully",
        "data": res,
    }


@router.post("/conversion")
async def log_conversion(
    payload: ConversionLogRequestSchema,
    db: Session = Depends(get_db),
):
    """Conversion webhook / callback log endpoint."""
    res = conversion_tracker_engine.record_conversion(
        db=db,
        provider_key=payload.provider_key,
        sale_amount=payload.sale_amount_inr,
        commission_amount=payload.commission_amount_inr,
        order_id=payload.order_id,
        click_id=payload.click_id,
    )
    return {
        "success": True,
        "message": "Conversion recorded successfully",
        "data": res,
    }


@router.get("/dashboard")
async def get_commission_dashboard(db: Session = Depends(get_db)):
    """Fetch Commission Dashboard analytics."""
    dashboard = affiliate_platform_service.get_commission_dashboard(db)
    return {
        "success": True,
        "message": "Commission dashboard retrieved",
        "data": dashboard.model_dump(),
    }


@router.get("/providers")
async def get_providers():
    """List registered affiliate providers and health status."""
    providers = provider_registry.get_all_providers()
    data = [
        {"key": p.provider_key, "name": p.name, "health": "healthy" if p.health_check() else "unhealthy"}
        for p in providers.values()
    ]
    return {
        "success": True,
        "message": "Registered affiliate providers retrieved",
        "data": {"providers": data},
    }


@router.get("/disclosure")
async def get_disclosure():
    """Fetch transparent user disclosure notice."""
    disclosure = affiliate_platform_service.get_user_disclosure()
    return {
        "success": True,
        "message": "Affiliate disclosure retrieved",
        "data": disclosure,
    }


@router.get("/metrics")
async def get_metrics():
    """Fetch Prometheus-compatible telemetry & latency metrics."""
    summary = affiliate_metrics.get_metrics_summary()
    return {
        "success": True,
        "message": "Affiliate Platform metrics retrieved",
        "data": summary,
    }


@router.get("/health")
async def affiliate_health():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "Enterprise Affiliate Commerce Platform operational",
        "data": {
            "status": "healthy",
            "version": "v11.0-enterprise-affiliate-platform",
        },
    }
