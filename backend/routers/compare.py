"""
Brand Battle - Comparison Router
Product comparison engine with AI-powered analysis and community voting.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional, List
import re

from database import get_db
from models import Product, Price, Comparison, Vote, User
from schemas import (
    ComparisonCreate, ComparisonResponse, ComparisonDetailResponse,
    ProductResponse, PriceResponse, VoteCreate, VoteResultResponse
)
from auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/api/compare", tags=["Comparisons"])


def generate_comparison_slug(products: List[Product]) -> str:
    """Generate a URL-friendly slug from product names."""
    names = [re.sub(r'[^a-z0-9]+', '-', p.name.lower()).strip('-') for p in products]
    return "-vs-".join(names)


def generate_feature_comparison(products: List[Product]) -> dict:
    """Generate feature-by-feature comparison data."""
    all_specs = {}

    # Collect all specification keys from all products
    for product in products:
        if product.specifications:
            for key in product.specifications:
                if key not in all_specs:
                    all_specs[key] = {}
                all_specs[key][product.id] = product.specifications[key]

    return all_specs


def determine_winners(products: List[Product], prices_map: dict) -> dict:
    """Determine winner for each comparison category."""
    winners = {}

    # Best Price
    price_products = [(p, prices_map.get(p.id, [])) for p in products]
    best_price_product = None
    best_price = float('inf')
    for product, prices in price_products:
        if product.current_best_price and product.current_best_price < best_price:
            best_price = product.current_best_price
            best_price_product = product

    if best_price_product:
        winners["Best Price"] = best_price_product.id

    # Best Rating
    rated = [(p, p.average_rating) for p in products if p.average_rating]
    if rated:
        winners["Best Rating"] = max(rated, key=lambda x: x[1])[0].id

    # Most Reviews
    reviewed = [(p, p.total_reviews) for p in products if p.total_reviews]
    if reviewed:
        winners["Most Reviewed"] = max(reviewed, key=lambda x: x[1])[0].id

    # Best Deal Score
    scored = [(p, p.deal_score) for p in products if p.deal_score]
    if scored:
        winners["Best Deal"] = max(scored, key=lambda x: x[1])[0].id

    # Extract spec-based winners (from specifications JSON)
    spec_keys_numeric = {}
    for product in products:
        if product.specifications:
            for key, value in product.specifications.items():
                if isinstance(value, (int, float)):
                    if key not in spec_keys_numeric:
                        spec_keys_numeric[key] = []
                    spec_keys_numeric[key].append((product.id, value))

    for key, entries in spec_keys_numeric.items():
        if len(entries) > 1:
            # Higher is better for most specs (battery, RAM, etc.)
            winner = max(entries, key=lambda x: x[1])
            winners[f"Best {key}"] = winner[0]

    return winners


def generate_ai_summary(products: List[Product], winners: dict) -> str:
    """Generate an AI comparison summary."""
    if len(products) < 2:
        return "Not enough products to compare."

    names = [p.name for p in products]
    summary_parts = [f"**Comparing {' vs '.join(names)}**\n"]

    # Overall winner (most category wins)
    from collections import Counter
    win_counts = Counter(winners.values())

    if win_counts:
        overall_winner_id = win_counts.most_common(1)[0][0]
        overall_winner = next((p for p in products if p.id == overall_winner_id), None)

        if overall_winner:
            total_categories = len(winners)
            wins = win_counts[overall_winner_id]
            summary_parts.append(
                f"🏆 **Overall Winner: {overall_winner.name}** — Wins {wins} out of {total_categories} categories.\n"
            )

    # Category breakdowns
    for category, product_id in winners.items():
        winner = next((p for p in products if p.id == product_id), None)
        if winner:
            summary_parts.append(f"• **{category}**: {winner.name}")

    # Price comparison
    price_info = []
    for p in products:
        if p.current_best_price:
            platform = p.current_best_platform or "available"
            price_info.append(f"{p.name}: ${p.current_best_price:.2f} ({platform})")

    if price_info:
        summary_parts.append(f"\n💰 **Price Comparison**:")
        for info in price_info:
            summary_parts.append(f"• {info}")

    # Rating comparison
    rating_info = []
    for p in products:
        if p.average_rating:
            rating_info.append(f"{p.name}: {p.average_rating:.1f}/5 ({p.total_reviews} reviews)")

    if rating_info:
        summary_parts.append(f"\n⭐ **Ratings**:")
        for info in rating_info:
            summary_parts.append(f"• {info}")

    # Recommendation
    summary_parts.append("\n---")
    if win_counts:
        overall_winner = next((p for p in products if p.id == win_counts.most_common(1)[0][0]), None)
        if overall_winner:
            summary_parts.append(
                f"\n**Recommendation**: If you value overall performance, go with **{overall_winner.name}**. "
                f"However, if budget is your primary concern, compare the prices above and consider deals on each platform."
            )

    return "\n".join(summary_parts)


@router.post("", response_model=ComparisonDetailResponse)
async def create_comparison(
    data: ComparisonCreate,
    db: Session = Depends(get_db),
):
    """Create or fetch a product comparison."""
    # Fetch products
    products = (
        db.query(Product)
        .filter(Product.id.in_(data.product_ids), Product.is_active == True)
        .options(joinedload(Product.brand), joinedload(Product.category))
        .all()
    )

    if len(products) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 valid products required for comparison"
        )

    # Generate slug
    slug = generate_comparison_slug(products)

    # Check if comparison already exists
    existing = db.query(Comparison).filter(Comparison.slug == slug).first()

    # Fetch prices for all products
    prices_map = {}
    for product in products:
        prices = (
            db.query(Price)
            .filter(Price.product_id == product.id, Price.is_available == True)
            .order_by(Price.price.asc())
            .all()
        )
        prices_map[product.id] = prices

    # Generate comparison data
    feature_comparison = generate_feature_comparison(products)
    winners = determine_winners(products, prices_map)
    ai_summary = generate_ai_summary(products, winners)

    # Determine overall winner
    from collections import Counter
    win_counts = Counter(winners.values())
    winner_id = win_counts.most_common(1)[0][0] if win_counts else None

    if existing:
        # Update existing comparison
        existing.ai_summary = ai_summary
        existing.feature_scores = feature_comparison
        existing.winner_id = winner_id
        existing.view_count += 1
        db.commit()
        comparison = existing
    else:
        # Create new comparison
        comparison = Comparison(
            slug=slug,
            title=" vs ".join([p.name for p in products]),
            product_ids=data.product_ids,
            winner_id=winner_id,
            ai_summary=ai_summary,
            feature_scores=feature_comparison,
        )
        db.add(comparison)
        db.commit()
        db.refresh(comparison)

    # Increment compare count for products
    for product in products:
        product.compare_count += 1
    db.commit()

    # Get vote results
    vote_results = {}
    if comparison.id:
        votes = (
            db.query(Vote.product_id, func.count(Vote.id))
            .filter(Vote.comparison_id == comparison.id)
            .group_by(Vote.product_id)
            .all()
        )
        vote_results = {product_id: count for product_id, count in votes}

    return ComparisonDetailResponse(
        comparison=ComparisonResponse.model_validate(comparison),
        products=[ProductResponse.model_validate(p) for p in products],
        prices={
            pid: [PriceResponse.model_validate(pr) for pr in prs]
            for pid, prs in prices_map.items()
        },
        feature_comparison=feature_comparison,
        winners=winners,
        ai_summary=ai_summary,
        vote_results=vote_results,
    )


@router.get("/trending", response_model=List[ComparisonResponse])
async def get_trending_comparisons(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get trending comparisons."""
    comparisons = (
        db.query(Comparison)
        .filter(Comparison.is_trending == True)
        .order_by(desc(Comparison.view_count))
        .limit(limit)
        .all()
    )

    # Fallback to most viewed if no trending
    if not comparisons:
        comparisons = (
            db.query(Comparison)
            .order_by(desc(Comparison.view_count))
            .limit(limit)
            .all()
        )

    return [ComparisonResponse.model_validate(c) for c in comparisons]


@router.get("/{comparison_id}", response_model=ComparisonDetailResponse)
async def get_comparison(
    comparison_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get comparison detail by ID."""
    comparison = db.query(Comparison).filter(Comparison.id == comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")

    comparison.view_count += 1
    db.commit()

    # Fetch products
    products = (
        db.query(Product)
        .filter(Product.id.in_(comparison.product_ids))
        .options(joinedload(Product.brand), joinedload(Product.category))
        .all()
    )

    # Fetch prices
    prices_map = {}
    for product in products:
        prices = (
            db.query(Price)
            .filter(Price.product_id == product.id, Price.is_available == True)
            .order_by(Price.price.asc())
            .all()
        )
        prices_map[product.id] = prices

    feature_comparison = generate_feature_comparison(products)
    winners = determine_winners(products, prices_map)

    # Vote results
    votes = (
        db.query(Vote.product_id, func.count(Vote.id))
        .filter(Vote.comparison_id == comparison.id)
        .group_by(Vote.product_id)
        .all()
    )
    vote_results = {product_id: count for product_id, count in votes}

    return ComparisonDetailResponse(
        comparison=ComparisonResponse.model_validate(comparison),
        products=[ProductResponse.model_validate(p) for p in products],
        prices={
            pid: [PriceResponse.model_validate(pr) for pr in prs]
            for pid, prs in prices_map.items()
        },
        feature_comparison=feature_comparison,
        winners=winners,
        ai_summary=comparison.ai_summary or "",
        vote_results=vote_results,
    )


@router.post("/vote", response_model=VoteResultResponse)
async def vote_on_comparison(
    vote_data: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Vote on which product is better in a comparison."""
    # Verify comparison exists
    comparison = db.query(Comparison).filter(Comparison.id == vote_data.comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")

    # Check if user already voted
    existing_vote = (
        db.query(Vote)
        .filter(
            Vote.user_id == current_user.id,
            Vote.comparison_id == vote_data.comparison_id,
        )
        .first()
    )

    if existing_vote:
        # Update vote
        existing_vote.product_id = vote_data.product_id
    else:
        # Create new vote
        vote = Vote(
            user_id=current_user.id,
            comparison_id=vote_data.comparison_id,
            product_id=vote_data.product_id,
        )
        db.add(vote)

    db.commit()

    # Get updated results
    votes = (
        db.query(Vote.product_id, func.count(Vote.id))
        .filter(Vote.comparison_id == vote_data.comparison_id)
        .group_by(Vote.product_id)
        .all()
    )
    results = {pid: count for pid, count in votes}
    total = sum(results.values())

    return VoteResultResponse(
        comparison_id=vote_data.comparison_id,
        results=results,
        total_votes=total,
        user_vote=vote_data.product_id,
    )
