"""
Brand Battle — Enterprise Notification Platform REST API Layer
FastAPI router mounted at /api/notifications/* exposing notification feeds, daily digests, preference center, and feedback endpoints.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_optional
from models import User
from notification_platform.services import notification_platform_service
from notification_platform.metrics import notification_metrics
from notification_platform.analytics import notification_analytics
from notification_platform.repository import notification_repo
from notification_platform.schemas import NotificationPreferenceSchema, NotificationFeedbackSchema

router = APIRouter(prefix="/api/notifications", tags=["Notification Platform"])


@router.get("")
async def get_notifications(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Fetch user in-app notification feed (sorted by value and relevance)."""
    user_id = current_user.id if current_user else 1
    feed = notification_platform_service.get_user_feed(db, user_id, limit=limit)
    return {
        "success": True,
        "message": f"Retrieved {len(feed)} notifications",
        "data": {"notifications": feed, "unread_count": sum(1 for n in feed if not n["is_read"])},
    }


@router.post("/read/{notification_id}")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Mark notification as read across devices (Cross-Device Synchronization)."""
    user_id = current_user.id if current_user else 1
    res = notification_platform_service.mark_notification_read(db, user_id, notification_id)
    return {
        "success": True,
        "message": f"Notification #{notification_id} marked as read",
        "data": res,
    }


@router.get("/digest")
async def get_daily_digest(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Fetch or generate Daily AI Digest summary."""
    user_id = current_user.id if current_user else 1
    digest = notification_platform_service.get_daily_digest(db, user_id)
    return {
        "success": True,
        "message": "Daily AI Digest generated",
        "data": digest,
    }


@router.get("/preferences")
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Fetch user Notification Preference Center settings."""
    user_id = current_user.id if current_user else 1
    prefs = notification_repo.get_or_create_preferences(db, user_id)
    return {
        "success": True,
        "message": "Preferences retrieved",
        "data": {
            "enable_in_app": prefs.enable_in_app,
            "enable_email": prefs.enable_email,
            "enable_push": prefs.enable_push,
            "enable_daily_digest": prefs.enable_daily_digest,
            "digest_frequency": prefs.digest_frequency,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "max_daily_notifications": prefs.max_daily_notifications,
        },
    }


@router.put("/preferences")
async def update_preferences(
    payload: NotificationPreferenceSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Update user Notification Preference Center settings."""
    user_id = current_user.id if current_user else 1
    res = notification_platform_service.update_user_preferences(db, user_id, payload.model_dump())
    return {
        "success": True,
        "message": "User preferences updated successfully",
        "data": res,
    }


@router.post("/feedback")
async def record_feedback(
    payload: NotificationFeedbackSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Submit helpfulness feedback to continuously optimize Happiness Index."""
    user_id = current_user.id if current_user else 1
    res = notification_platform_service.record_feedback(
        db, user_id, payload.notification_id, payload.is_helpful, payload.feedback_text
    )
    return {
        "success": True,
        "message": "Feedback recorded; Happiness Index updated",
        "data": res,
    }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Retrieve observability metrics & Happiness Index telemetry."""
    summary = notification_metrics.get_metrics_summary()
    happiness = notification_analytics.calculate_happiness_metric(db)
    summary["happiness_analytics"] = happiness
    return {
        "success": True,
        "message": "Notification Platform metrics retrieved",
        "data": summary,
    }


@router.post("/price-alerts/check")
async def check_price_alert(
    product_id: int,
    current_price: float,
    target_price: float,
    last_notified_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Target Price Monitoring Worker endpoint evaluating price threshold reach and re-arm logic."""
    from models import Product
    from notification_platform.price_alerts import price_drop_intelligence

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        class MockProd:
            id = product_id
            name = f"Product #{product_id}"
        product = MockProd()

    res = price_drop_intelligence.evaluate_target_price_alert(
        product=product,
        current_price=current_price,
        target_price=target_price,
        last_notified_price=last_notified_price,
    )

    return {
        "success": True,
        "message": "Price alert check completed",
        "data": res or {"should_notify": False, "reason": "Target price not reached or cooldown active"},
    }


@router.get("/health")
async def notification_health():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "Notification Intelligence Platform operational",
        "data": {
            "status": "healthy",
            "version": "v6.0.0-enterprise-notification-intelligence",
        },
    }
