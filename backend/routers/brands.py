"""
Brand Battle - Brands Router
Brand listing, detail, and reputation scores.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List

from database import get_db
from models import Brand, Product
from schemas import BrandResponse, ProductResponse

router = APIRouter(prefix="/api/brands", tags=["Brands"])


@router.get("", response_model=List[BrandResponse])
async def list_brands(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "trust_score",
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List all brands with optional filtering."""
    q = db.query(Brand)

    if category:
        q = q.filter(Brand.category == category)

    if search:
        q = q.filter(Brand.name.ilike(f"%{search}%"))

    if sort_by == "name":
        q = q.order_by(Brand.name)
    elif sort_by == "trust_score":
        q = q.order_by(desc(Brand.trust_score))

    brands = q.limit(limit).all()
    return [BrandResponse.model_validate(b) for b in brands]


@router.get("/{brand_slug}", response_model=BrandResponse)
async def get_brand(brand_slug: str, db: Session = Depends(get_db)):
    """Get brand detail by slug."""
    brand = db.query(Brand).filter(Brand.slug == brand_slug).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return BrandResponse.model_validate(brand)


@router.get("/{brand_slug}/products", response_model=List[ProductResponse])
async def get_brand_products(
    brand_slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all products for a brand."""
    brand = db.query(Brand).filter(Brand.slug == brand_slug).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    offset = (page - 1) * page_size
    products = (
        db.query(Product)
        .filter(Product.brand_id == brand.id, Product.is_active == True)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{brand_slug}/reputation")
async def get_brand_reputation(brand_slug: str, db: Session = Depends(get_db)):
    """Get detailed brand reputation breakdown."""
    brand = db.query(Brand).filter(Brand.slug == brand_slug).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return {
        "brand": BrandResponse.model_validate(brand),
        "reputation": {
            "overall_trust_score": brand.trust_score,
            "customer_satisfaction": brand.customer_satisfaction,
            "return_rate": brand.return_rate,
            "review_sentiment": brand.review_sentiment,
            "durability_score": brand.durability_score,
        },
        "verdict": (
            "Highly Trusted" if brand.trust_score >= 8
            else "Trusted" if brand.trust_score >= 6
            else "Average" if brand.trust_score >= 4
            else "Below Average"
        ),
    }
