"""
Brand Battle - Admin Router
Admin dashboard: product management, analytics, and system overview.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database import get_db
from models import (
    User, Product, Brand, Deal, PriceAlert, SearchHistory,
    Comparison, AnalyticsEvent, AffiliateLink, Notification
)
from schemas import AnalyticsSummary, ProductResponse, BrandResponse
from auth import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard", response_model=AnalyticsSummary)
async def get_dashboard(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get admin dashboard analytics summary."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0
    total_searches = db.query(func.count(SearchHistory.id)).scalar() or 0
    total_comparisons = db.query(func.count(Comparison.id)).scalar() or 0
    total_deals = db.query(func.count(Deal.id)).filter(Deal.status == "active").scalar() or 0
    active_alerts = db.query(func.count(PriceAlert.id)).filter(PriceAlert.status == "active").scalar() or 0

    # Top searches
    top_searches_q = (
        db.query(SearchHistory.query, func.count(SearchHistory.id).label("count"))
        .group_by(SearchHistory.query)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    top_searches = [{"query": s.query, "count": s.count} for s in top_searches_q]

    # Top products by views
    top_products_q = (
        db.query(Product)
        .filter(Product.is_active == True)
        .order_by(desc(Product.view_count))
        .limit(10)
        .all()
    )
    top_products = [
        {"id": p.id, "name": p.name, "views": p.view_count, "compares": p.compare_count}
        for p in top_products_q
    ]

    # Total affiliate revenue
    revenue = db.query(func.sum(AffiliateLink.revenue)).scalar() or 0

    return AnalyticsSummary(
        total_users=total_users,
        total_products=total_products,
        total_searches=total_searches,
        total_comparisons=total_comparisons,
        total_deals=total_deals,
        active_alerts=active_alerts,
        top_searches=top_searches,
        top_products=top_products,
        revenue=round(revenue, 2),
    )


@router.get("/products")
async def admin_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all products for admin management."""
    offset = (page - 1) * page_size
    total = db.query(func.count(Product.id)).scalar() or 0

    products = (
        db.query(Product)
        .order_by(desc(Product.created_at))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "products": [ProductResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/brands")
async def admin_list_brands(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all brands."""
    brands = db.query(Brand).order_by(Brand.name).all()
    return [BrandResponse.model_validate(b) for b in brands]


@router.get("/users")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    offset = (page - 1) * page_size
    total = db.query(func.count(User.id)).scalar() or 0

    users = (
        db.query(User)
        .order_by(desc(User.created_at))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": str(u.created_at) if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/analytics/searches")
async def admin_search_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get search analytics over time."""
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Searches per day
    daily_searches = (
        db.query(
            func.date(SearchHistory.created_at).label("date"),
            func.count(SearchHistory.id).label("count"),
        )
        .filter(SearchHistory.created_at >= since)
        .group_by(func.date(SearchHistory.created_at))
        .order_by("date")
        .all()
    )

    return {
        "daily_searches": [
            {"date": str(s.date), "count": s.count}
            for s in daily_searches
        ]
    }
