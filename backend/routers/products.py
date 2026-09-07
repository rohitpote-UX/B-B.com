"""
Brand Battle - Products Router
Product search, detail, prices, deals, and reviews endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, desc
from typing import Optional, List

from database import get_db
from models import Product, Price, PriceHistory, Review, Brand, Category, SearchHistory
from schemas import (
    ProductResponse, ProductListResponse, PriceResponse,
    PriceHistoryResponse, PriceHistoryListResponse,
    ReviewResponse, ReviewSummaryResponse, ProductSearchQuery
)
from auth import get_current_user_optional, get_current_user
from models import User

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/search", response_model=ProductListResponse)
@router.get("", response_model=ProductListResponse)
@router.get("/", response_model=ProductListResponse)
async def search_products(
    query: str = "",
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "relevance",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Search products with filters and pagination."""
    q = db.query(Product).filter(Product.is_active == True)

    # Text search
    if query:
        search_filter = or_(
            Product.name.ilike(f"%{query}%"),
            Product.description.ilike(f"%{query}%"),
            Product.short_description.ilike(f"%{query}%"),
        )
        q = q.filter(search_filter)

        # Log search history
        search_log = SearchHistory(
            user_id=current_user.id if current_user else None,
            query=query,
        )
        db.add(search_log)
        db.commit()

    # Category filter
    if category:
        q = q.join(Category).filter(Category.slug == category)

    # Brand filter
    if brand:
        q = q.join(Brand).filter(Brand.slug == brand)

    # Price range
    if min_price is not None:
        q = q.filter(Product.current_best_price >= min_price)
    if max_price is not None:
        q = q.filter(Product.current_best_price <= max_price)

    # Rating filter
    if min_rating is not None:
        q = q.filter(Product.average_rating >= min_rating)

    # Get total count
    total = q.count()

    # Sorting
    if sort_by == "price_asc":
        q = q.order_by(Product.current_best_price.asc().nullslast())
    elif sort_by == "price_desc":
        q = q.order_by(Product.current_best_price.desc().nullslast())
    elif sort_by == "rating":
        q = q.order_by(Product.average_rating.desc())
    elif sort_by == "newest":
        q = q.order_by(Product.created_at.desc())
    elif sort_by == "popular":
        q = q.order_by(Product.view_count.desc())
    else:  # relevance - boost by rating and views
        q = q.order_by(
            desc(Product.average_rating * 0.6 + Product.view_count * 0.0001)
        )

    # Pagination
    offset = (page - 1) * page_size
    products = q.options(
        joinedload(Product.brand),
        joinedload(Product.category)
    ).offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/trending", response_model=List[ProductResponse])
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get trending products based on views and comparisons."""
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .order_by(desc(Product.view_count + Product.compare_count))
        .options(joinedload(Product.brand), joinedload(Product.category))
        .limit(limit)
        .all()
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/top-rated", response_model=List[ProductResponse])
async def get_top_rated_products(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get top rated products."""
    q = db.query(Product).filter(
        Product.is_active == True,
        Product.average_rating > 0,
        Product.total_reviews >= 5,
    )

    if category:
        q = q.join(Category).filter(Category.slug == category)

    products = (
        q.order_by(desc(Product.average_rating))
        .options(joinedload(Product.brand), joinedload(Product.category))
        .limit(limit)
        .all()
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Get product detail by ID."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .options(joinedload(Product.brand), joinedload(Product.category))
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Increment view count
    product.view_count += 1
    db.commit()

    return ProductResponse.model_validate(product)


@router.get("/{product_id}/prices", response_model=List[PriceResponse])
async def get_product_prices(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Get current prices across all platforms for a product."""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prices = (
        db.query(Price)
        .filter(Price.product_id == product_id, Price.is_available == True)
        .order_by(Price.price.asc())
        .all()
    )

    return [PriceResponse.model_validate(p) for p in prices]


@router.get("/{product_id}/price-history", response_model=PriceHistoryListResponse)
async def get_price_history(
    product_id: int,
    platform: Optional[str] = None,
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """Get price history for a product over time."""
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(days=days)

    q = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.recorded_at >= since,
    )

    if platform:
        q = q.filter(PriceHistory.platform == platform)

    history = q.order_by(PriceHistory.recorded_at.asc()).all()

    if not history:
        return PriceHistoryListResponse(
            history=[],
            lowest_price=0,
            highest_price=0,
            average_price=0,
            best_time_to_buy=None,
        )

    prices = [h.price for h in history]
    lowest = min(prices)
    highest = max(prices)
    average = sum(prices) / len(prices)

    # Determine best time to buy (month with lowest average price)
    from collections import defaultdict
    monthly_prices = defaultdict(list)
    for h in history:
        if h.recorded_at:
            month_name = h.recorded_at.strftime("%B")
            monthly_prices[month_name].append(h.price)

    best_month = None
    if monthly_prices:
        best_month = min(monthly_prices, key=lambda m: sum(monthly_prices[m]) / len(monthly_prices[m]))

    return PriceHistoryListResponse(
        history=[PriceHistoryResponse.model_validate(h) for h in history],
        lowest_price=lowest,
        highest_price=highest,
        average_price=round(average, 2),
        best_time_to_buy=best_month,
    )


@router.get("/{product_id}/reviews", response_model=ReviewSummaryResponse)
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get aggregated reviews with AI summary for a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get reviews
    offset = (page - 1) * page_size
    reviews = (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.helpful_count.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Calculate rating distribution
    all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    all_pros = []
    all_cons = []

    for r in all_reviews:
        if r.rating:
            bucket = str(min(5, max(1, round(r.rating))))
            distribution[bucket] = distribution.get(bucket, 0) + 1
        if r.pros:
            all_pros.extend(r.pros)
        if r.cons:
            all_cons.extend(r.cons)

    # Top pros/cons by frequency
    from collections import Counter
    top_pros = [item for item, _ in Counter(all_pros).most_common(5)]
    top_cons = [item for item, _ in Counter(all_cons).most_common(5)]
    common_complaints = [item for item, count in Counter(all_cons).most_common(3) if count > 1]

    # Generate AI summary
    avg_rating = product.average_rating or 0
    total = len(all_reviews)
    ai_summary = (
        f"Based on {total} reviews across multiple platforms, this product has an "
        f"average rating of {avg_rating:.1f}/5. "
    )
    if top_pros:
        ai_summary += f"Users frequently praise: {', '.join(top_pros[:3])}. "
    if top_cons:
        ai_summary += f"Common concerns include: {', '.join(top_cons[:3])}. "
    if avg_rating >= 4.0:
        ai_summary += "Overall, this product is highly recommended by the community."
    elif avg_rating >= 3.0:
        ai_summary += "This product receives mixed but generally positive reviews."
    else:
        ai_summary += "Users have reported significant issues — consider alternatives."

    return ReviewSummaryResponse(
        total_reviews=total,
        average_rating=round(avg_rating, 1),
        rating_distribution=distribution,
        top_pros=top_pros,
        top_cons=top_cons,
        common_complaints=common_complaints,
        ai_summary=ai_summary,
        reviews=[ReviewResponse.model_validate(r) for r in reviews],
    )
