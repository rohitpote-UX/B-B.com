"""
Brand Battle - Deals Router
Active deals, best deals, and deal quality analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime, timezone

from database import get_db
from models import Deal, Product, Price
from schemas import DealResponse, DealListResponse, ProductResponse

router = APIRouter(prefix="/api/deals", tags=["Deals"])


@router.get("", response_model=DealListResponse)
async def get_deals(
    category: Optional[str] = None,
    platform: Optional[str] = None,
    min_discount: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "deal_score",  # deal_score, discount, price, newest
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get active deals with filters."""
    q = db.query(Deal).filter(Deal.status == "active")

    # Platform filter
    if platform:
        q = q.filter(Deal.platform == platform)

    # Discount filter
    if min_discount:
        q = q.filter(Deal.discount_percentage >= min_discount)

    # Price filter
    if max_price:
        q = q.filter(Deal.deal_price <= max_price)

    # Get total
    total = q.count()

    # Sorting
    if sort_by == "discount":
        q = q.order_by(desc(Deal.discount_percentage))
    elif sort_by == "price":
        q = q.order_by(Deal.deal_price.asc())
    elif sort_by == "newest":
        q = q.order_by(desc(Deal.created_at))
    else:  # deal_score
        q = q.order_by(desc(Deal.deal_score))

    # Pagination
    offset = (page - 1) * page_size
    deals = q.offset(offset).limit(page_size).all()

    # Enrich with product data
    deal_responses = []
    for deal in deals:
        product = db.query(Product).filter(Product.id == deal.product_id).first()
        deal_resp = DealResponse.model_validate(deal)
        if product:
            deal_resp.product = ProductResponse.model_validate(product)
        deal_responses.append(deal_resp)

    return DealListResponse(
        deals=deal_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/best", response_model=List[DealResponse])
async def get_best_deals(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get the best deals based on deal quality score."""
    deals = (
        db.query(Deal)
        .filter(
            Deal.status == "active",
            Deal.is_fake_discount == False,
            Deal.deal_score >= 70,
        )
        .order_by(desc(Deal.deal_score))
        .limit(limit)
        .all()
    )

    deal_responses = []
    for deal in deals:
        product = db.query(Product).filter(Product.id == deal.product_id).first()
        deal_resp = DealResponse.model_validate(deal)
        if product:
            deal_resp.product = ProductResponse.model_validate(product)
        deal_responses.append(deal_resp)

    return deal_responses


@router.get("/platforms")
async def get_platform_stats(db: Session = Depends(get_db)):
    """Get deal statistics per platform."""
    stats = (
        db.query(
            Deal.platform,
            func.count(Deal.id).label("total_deals"),
            func.avg(Deal.discount_percentage).label("avg_discount"),
            func.avg(Deal.deal_score).label("avg_deal_score"),
        )
        .filter(Deal.status == "active")
        .group_by(Deal.platform)
        .all()
    )

    return [
        {
            "platform": s.platform,
            "total_deals": s.total_deals,
            "avg_discount": round(s.avg_discount or 0, 1),
            "avg_deal_score": round(s.avg_deal_score or 0, 1),
        }
        for s in stats
    ]


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get deal detail by ID."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal.view_count += 1
    db.commit()

    product = db.query(Product).filter(Product.id == deal.product_id).first()
    deal_resp = DealResponse.model_validate(deal)
    if product:
        deal_resp.product = ProductResponse.model_validate(product)

    return deal_resp
