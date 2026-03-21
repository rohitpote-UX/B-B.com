"""
Brand Battle - Alerts Router
Price alert creation, management, and notification preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import PriceAlert, Product, Notification, User
from schemas import AlertCreate, AlertResponse, NotificationResponse, ProductResponse
from auth import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["Price Alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new price alert for a product."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == alert_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check for existing alert
    existing = (
        db.query(PriceAlert)
        .filter(
            PriceAlert.user_id == current_user.id,
            PriceAlert.product_id == alert_data.product_id,
            PriceAlert.status == "active",
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Active alert already exists for this product",
        )

    alert = PriceAlert(
        user_id=current_user.id,
        product_id=alert_data.product_id,
        target_price=alert_data.target_price,
        current_price=product.current_best_price,
        platform=alert_data.platform,
        notify_email=alert_data.notify_email,
        notify_push=alert_data.notify_push,
        notify_browser=alert_data.notify_browser,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    alert_resp = AlertResponse.model_validate(alert)
    alert_resp.product = ProductResponse.model_validate(product)

    return alert_resp


@router.get("", response_model=List[AlertResponse])
async def get_my_alerts(
    status_filter: str = Query("active", alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all alerts for the current user."""
    q = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id)

    if status_filter != "all":
        q = q.filter(PriceAlert.status == status_filter)

    alerts = q.order_by(PriceAlert.created_at.desc()).all()

    alert_responses = []
    for alert in alerts:
        product = db.query(Product).filter(Product.id == alert.product_id).first()
        alert_resp = AlertResponse.model_validate(alert)
        if product:
            alert_resp.product = ProductResponse.model_validate(product)
        alert_responses.append(alert_resp)

    return alert_responses


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a price alert."""
    alert = (
        db.query(PriceAlert)
        .filter(PriceAlert.id == alert_id, PriceAlert.user_id == current_user.id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()


@router.put("/{alert_id}/pause", response_model=AlertResponse)
async def pause_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pause an active price alert."""
    alert = (
        db.query(PriceAlert)
        .filter(PriceAlert.id == alert_id, PriceAlert.user_id == current_user.id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "paused" if alert.status == "active" else "active"
    db.commit()
    db.refresh(alert)

    return AlertResponse.model_validate(alert)


# ─── Notifications ───────────────────────────────────────────────────

notifications_router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@notifications_router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notifications for the current user."""
    q = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        q = q.filter(Notification.is_read == False)

    offset = (page - 1) * page_size
    notifications = (
        q.order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return [NotificationResponse.model_validate(n) for n in notifications]


@notifications_router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()

    return {"message": "Marked as read"}


@notifications_router.put("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return {"message": "All notifications marked as read"}


@notifications_router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get count of unread notifications."""
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .count()
    )

    return {"unread_count": count}
