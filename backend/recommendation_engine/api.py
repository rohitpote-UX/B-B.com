"""
Brand Battle — Recommendation Platform REST API Layer
Exposes high-performance FastAPI endpoints for product recommendations, value scores, trending items, feedback, and observability metrics.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from recommendation_engine.recommendation_service import recommendation_orchestrator
from recommendation_engine.recommendation_metrics import recommendation_metrics_collector
from recommendation_engine.feedback_collector import feedback_collector_service
from recommendation_engine.ab_testing import ab_testing_allocator
from recommendation_engine.recommendation_history import recommendation_history_logger
from recommendation_engine.recommendation_config import recommendation_settings
from logging_config import logger

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/product/{product_id}")
async def get_product_recommendations(
    product_id: int,
    user_id: Optional[int] = Query(None, description="Optional logged-in user ID for personalization"),
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendation items to return"),
    db: Session = Depends(get_db)
):
    """Fetch multi-category AI recommendations for a specific product."""
    data = recommendation_orchestrator.get_product_recommendations(db, product_id, user_id=user_id, limit=limit)
    if data.get("status") == "error":
        raise HTTPException(status_code=404, detail=data.get("message", "Product not found"))
    
    return {
        "success": True,
        "message": f"Generated {len(data.get('recommendations', []))} AI recommendations for product #{product_id}",
        "data": data
    }


@router.get("/similar/{product_id}")
async def get_similar_recommendations(
    product_id: int,
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Fetch specification & hardware similarity recommendations."""
    data = recommendation_orchestrator.get_product_recommendations(db, product_id, limit=limit)
    return {
        "success": True,
        "message": "Similar specifications retrieved",
        "data": data
    }


@router.get("/value")
async def get_best_value_recommendations(
    category_id: Optional[int] = Query(None, description="Optional category filter"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Fetch platform-wide or category-specific Best Value & Editor's Choice products."""
    items = recommendation_orchestrator.get_best_value_products(db, category_id=category_id, limit=limit)
    return {
        "success": True,
        "message": "Best value recommendations retrieved",
        "data": {"total": len(items), "items": items}
    }


@router.get("/trending")
async def get_trending_recommendations(
    category_id: Optional[int] = Query(None, description="Optional category filter"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Fetch real-time trending products based on view velocity and momentum."""
    items = recommendation_orchestrator.get_trending_products(db, category_id=category_id, limit=limit)
    return {
        "success": True,
        "message": "Trending products retrieved",
        "data": {"total": len(items), "items": items}
    }


@router.get("/upgrades/{product_id}")
async def get_premium_upgrades(
    product_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Fetch premium hardware upgrade recommendations."""
    items = recommendation_orchestrator.get_premium_upgrades(db, product_id, limit=limit)
    return {
        "success": True,
        "message": "Premium upgrade recommendations retrieved",
        "data": {"total": len(items), "items": items}
    }


@router.get("/budget/{product_id}")
async def get_budget_alternatives(
    product_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Fetch budget-friendly alternative recommendations."""
    items = recommendation_orchestrator.get_budget_alternatives(db, product_id, limit=limit)
    return {
        "success": True,
        "message": "Budget alternative recommendations retrieved",
        "data": {"total": len(items), "items": items}
    }


@router.get("/frequently-compared/{product_id}")
async def get_frequently_compared(
    product_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Fetch products frequently compared with the target item."""
    data = recommendation_orchestrator.get_product_recommendations(db, product_id, limit=limit)
    return {
        "success": True,
        "message": "Frequently compared recommendations retrieved",
        "data": data
    }


@router.get("/accessories/{product_id}")
async def get_accessory_recommendations(
    product_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Fetch accessory and complementary recommendations."""
    items = recommendation_orchestrator.get_accessories(db, product_id, limit=limit)
    return {
        "success": True,
        "message": "Accessory recommendations retrieved",
        "data": {"total": len(items), "items": items}
    }


@router.post("/feedback")
async def record_recommendation_feedback(
    recommendation_id: str = Query(..., description="Unique recommendation ID"),
    product_id: int = Query(..., description="Product ID interacted with"),
    action: str = Query(..., description="Interaction action: clicked, compared, wishlisted, purchased, ignored"),
    user_id: Optional[int] = Query(None)
):
    """Record user feedback action on a recommendation item."""
    feedback_collector_service.record_feedback(recommendation_id, product_id, action, user_id=user_id)
    recommendation_metrics_collector.record_click()
    return {
        "success": True,
        "message": f"Recorded feedback action '{action}' for product #{product_id}",
        "data": {"recommendation_id": recommendation_id, "action": action}
    }


@router.get("/metrics")
async def get_recommendation_metrics():
    """Retrieve observability metrics and telemetry summary."""
    summary = recommendation_metrics_collector.get_telemetry_summary()
    return {
        "success": True,
        "message": "Recommendation platform telemetry summary retrieved",
        "data": summary
    }


@router.get("/ab-test")
async def get_ab_test_variant(
    session_id: str = Query("guest_session", description="Session or User ID")
):
    """Retrieve assigned A/B experiment variant and scoring configuration."""
    variant = ab_testing_allocator.assign_variant(session_id)
    variant_config = ab_testing_allocator.get_variant_config(variant)
    return {
        "success": True,
        "message": f"Assigned A/B experiment variant: {variant}",
        "data": variant_config
    }
