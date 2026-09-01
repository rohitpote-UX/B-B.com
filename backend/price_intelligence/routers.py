"""
Brand Battle — Enterprise Price Intelligence REST API Layer
FastAPI router mounted at /api/price-intelligence/* providing access to all 20 intelligence sub-engines.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_optional
from models import User
from price_intelligence.services import price_intel_service
from price_intelligence.alert_engine import smart_alert_engine
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.fake_discount_detector import fake_discount_detector
from price_intelligence.price_forecasting import price_forecasting_engine
from price_intelligence.ownership_cost import ownership_cost_engine
from price_intelligence.hidden_cost_calculator import hidden_cost_calculator
from price_intelligence.bundle_engine import smart_bundle_engine
from price_intelligence.best_time_to_buy import best_time_to_buy_engine
from price_intelligence.buy_advisor import ai_buy_advisor
from price_intelligence.metrics import price_intel_metrics
from price_intelligence.schemas import PriceAlertCreateSchema
from price_intelligence.repository import price_intel_repo

router = APIRouter(prefix="/api/price-intelligence", tags=["Price Intelligence"])


@router.get("/product/{product_id}")
async def get_price_intelligence_report(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Fetch comprehensive 20-module Enterprise AI Price Intelligence Report
    including buy advice, fair market value, fake discount audit, forecast, TCO, and bundles.
    """
    user_id = current_user.id if current_user else None
    report = price_intel_service.generate_full_report(db, product_id, user_id=user_id)

    if report.get("status") == "error":
        raise HTTPException(status_code=404, detail=report.get("message"))

    return {
        "success": True,
        "message": f"Generated Price Intelligence report for product #{product_id}",
        "data": report,
    }


@router.get("/buy-advice/{product_id}")
async def get_buy_advice(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch AI Buy Recommendation & Buy Confidence Score."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    buy_rec = ai_buy_advisor.advise_buy(db, product)
    return {
        "success": True,
        "message": "AI Buy Advice generated",
        "data": buy_rec.model_dump(),
    }


@router.get("/fair-value/{product_id}")
async def get_fair_value(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch Fair Market Value calculation and over/underpriced metrics."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    fv = fair_value_engine.calculate_fair_value(db, product)
    return {
        "success": True,
        "message": "Fair Market Value calculated",
        "data": fv.model_dump(),
    }


@router.get("/discount-audit/{product_id}")
async def audit_discount(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Audit discount integrity and detect MRP manipulation."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    audit = fake_discount_detector.audit_discount(db, product)
    return {
        "success": True,
        "message": "Discount audit complete",
        "data": audit.model_dump(),
    }


@router.get("/forecast/{product_id}")
async def forecast_prices(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch 7d, 30d, 90d, and festival AI price predictions."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    forecast = price_forecasting_engine.forecast_prices(db, product)
    return {
        "success": True,
        "message": "Price forecast generated",
        "data": forecast.model_dump(),
    }


@router.get("/best-time/{product_id}")
async def get_best_time_to_buy(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch optimal buying window and festival savings opportunities."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    best_time = best_time_to_buy_engine.evaluate_best_time(db, product)
    return {
        "success": True,
        "message": "Best time to buy evaluated",
        "data": best_time,
    }


@router.get("/ownership-cost/{product_id}")
async def get_ownership_cost(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch Total Cost of Ownership (TCO) and hidden cost calculations."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    tco = ownership_cost_engine.calculate_tco(product)
    hidden = hidden_cost_calculator.calculate_hidden_costs(product)
    return {
        "success": True,
        "message": "TCO and hidden costs calculated",
        "data": {
            "tco_3yr": tco.model_dump(),
            "hidden_costs": hidden.model_dump(),
        },
    }


@router.get("/bundles/{product_id}")
async def get_smart_bundles(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch smart complementary product bundle recommendations."""
    product = price_intel_repo.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    bundles = smart_bundle_engine.recommend_bundles(db, product)
    return {
        "success": True,
        "message": "Smart bundles generated",
        "data": [b.model_dump() for b in bundles],
    }


@router.post("/alerts")
async def create_price_alert(
    payload: PriceAlertCreateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Create a user price alert rule."""
    user_id = current_user.id if current_user else 1

    alert = smart_alert_engine.create_alert(
        db=db,
        user_id=user_id,
        product_id=payload.product_id,
        target_price=payload.target_price,
        notify_email=payload.notify_email,
        drop_percentage=payload.drop_percentage,
        marketplace_filter=payload.marketplace_filter,
    )

    return {
        "success": True,
        "message": f"Price alert rule created for product #{payload.product_id}",
        "data": {
            "alert_id": alert.id,
            "product_id": alert.product_id,
            "target_price": alert.target_price,
            "notify_email": alert.notify_email,
        },
    }


@router.get("/metrics")
async def get_metrics():
    """Observability telemetry summary endpoint."""
    return {
        "success": True,
        "message": "Price Intelligence metrics retrieved",
        "data": price_intel_metrics.get_metrics_summary(),
    }


@router.get("/health")
async def price_intel_health():
    """Health check endpoint."""
    from redis_client import is_redis_healthy
    return {
        "success": True,
        "message": "Price Intelligence Platform operational",
        "data": {
            "status": "healthy",
            "redis": "connected" if is_redis_healthy() else "disconnected",
            "version": "v5.0.0-enterprise-price-intelligence",
        },
    }
