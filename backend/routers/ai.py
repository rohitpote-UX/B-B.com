"""
Brand Battle - AI Router
AI-powered product recommendations, summaries, and natural language queries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
from typing import Optional, List

from database import get_db
from models import Product, Price, Brand, Category, User
from schemas import (
    AIRecommendRequest, AIRecommendResponse, AIRecommendation,
    AISummaryRequest, ProductResponse, CartOptimizerRequest,
    CartOptimizerResponse, CartOptimizerResult
)
from auth import get_current_user_optional

router = APIRouter(prefix="/api/ai", tags=["AI Engine"])


def parse_budget_from_query(query: str) -> Optional[float]:
    """Extract budget amount from natural language query."""
    import re
    # Match patterns like "under $1500", "below 50k", "under ₹50000", "budget 60k"
    patterns = [
        r'under\s*\$?\s*(\d+(?:\.\d+)?)\s*k?\b',
        r'below\s*\$?\s*(\d+(?:\.\d+)?)\s*k?\b',
        r'budget\s*:?\s*\$?\s*(\d+(?:\.\d+)?)\s*k?\b',
        r'within\s*\$?\s*(\d+(?:\.\d+)?)\s*k?\b',
        r'\$(\d+(?:\.\d+)?)\s*k?\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            amount = float(match.group(1))
            if 'k' in query.lower()[match.end()-2:match.end()+1]:
                amount *= 1000
            return amount
    return None


def extract_category_from_query(query: str) -> Optional[str]:
    """Extract product category from natural language query."""
    category_keywords = {
        'phone': 'smartphones',
        'mobile': 'smartphones',
        'smartphone': 'smartphones',
        'laptop': 'laptops',
        'notebook': 'laptops',
        'shoe': 'shoes',
        'sneaker': 'shoes',
        'shirt': 'clothing',
        'tshirt': 'clothing',
        't-shirt': 'clothing',
        'headphone': 'headphones',
        'earphone': 'headphones',
        'earbud': 'headphones',
        'watch': 'watches',
        'smartwatch': 'watches',
        'tablet': 'tablets',
        'camera': 'cameras',
        'tv': 'televisions',
        'television': 'televisions',
    }

    query_lower = query.lower()
    for keyword, category in category_keywords.items():
        if keyword in query_lower:
            return category
    return None


def score_product(product: Product, query: str, budget: Optional[float] = None) -> float:
    """Calculate recommendation score for a product."""
    score = 0.0

    # Rating score (0-30 points)
    if product.average_rating:
        score += product.average_rating * 6  # Max 30

    # Review count score (0-15 points)
    if product.total_reviews:
        score += min(15, product.total_reviews * 0.1)

    # Deal score (0-20 points)
    if product.deal_score:
        score += product.deal_score * 0.2

    # Price within budget bonus (0-20 points)
    if budget and product.current_best_price:
        if product.current_best_price <= budget:
            # Higher score for products closer to budget (better value)
            ratio = product.current_best_price / budget
            score += 20 * ratio  # Closer to budget = better value
        else:
            score -= 10  # Penalty for over budget

    # Popularity score (0-15 points)
    if product.view_count:
        score += min(15, product.view_count * 0.01)

    return round(score, 2)


def generate_product_reasoning(product: Product, rank: int, budget: Optional[float] = None) -> str:
    """Generate reasoning for why a product is recommended."""
    parts = []

    if rank == 1:
        parts.append(f"🏆 Top pick! {product.name} stands out as the best overall choice.")
    elif rank == 2:
        parts.append(f"Strong contender — {product.name} offers excellent value.")
    else:
        parts.append(f"Worth considering — {product.name} is a solid option.")

    if product.average_rating:
        if product.average_rating >= 4.5:
            parts.append(f"Exceptional rating of {product.average_rating:.1f}/5 from {product.total_reviews} reviews.")
        elif product.average_rating >= 4.0:
            parts.append(f"Strong rating of {product.average_rating:.1f}/5 across {product.total_reviews} reviews.")

    if budget and product.current_best_price:
        savings = budget - product.current_best_price
        if savings > 0:
            parts.append(f"${savings:.2f} under your budget — great value.")
        elif savings == 0:
            parts.append("Right at your budget limit.")

    if product.current_best_platform:
        parts.append(f"Best price currently available on {product.current_best_platform}.")

    if product.deal_score and product.deal_score >= 80:
        parts.append(f"Deal Score: {product.deal_score:.0f}/100 — this is a genuine deal.")

    return " ".join(parts)


def generate_pros_cons(product: Product) -> tuple:
    """Generate pros and cons for a product."""
    pros = []
    cons = []

    if product.average_rating:
        if product.average_rating >= 4.0:
            pros.append(f"High user rating ({product.average_rating:.1f}/5)")
        else:
            cons.append(f"Below average rating ({product.average_rating:.1f}/5)")

    if product.total_reviews:
        if product.total_reviews >= 100:
            pros.append(f"Well-reviewed ({product.total_reviews}+ reviews)")
        elif product.total_reviews < 10:
            cons.append("Limited reviews available")

    if product.deal_score:
        if product.deal_score >= 80:
            pros.append("Excellent deal quality")
        elif product.deal_score < 50:
            cons.append("Questionable deal — may not be genuine discount")

    if product.features:
        pros.extend(product.features[:2])

    if product.brand and hasattr(product.brand, 'trust_score'):
        if product.brand.trust_score >= 8:
            pros.append(f"Trusted brand (Score: {product.brand.trust_score}/10)")

    # Default pros/cons if empty
    if not pros:
        pros = ["Available across multiple platforms", "Competitive pricing"]
    if not cons:
        cons = ["Specs may vary by variant", "Prices subject to change"]

    return pros[:5], cons[:4]


@router.post("/recommend", response_model=AIRecommendResponse)
async def get_recommendations(
    request: AIRecommendRequest,
    db: Session = Depends(get_db),
):
    """Get AI-powered product recommendations based on natural language query."""
    query = request.query
    budget = request.budget or parse_budget_from_query(query)
    category = extract_category_from_query(query)

    # Build query
    q = db.query(Product).filter(Product.is_active == True)

    # Category filter
    if category:
        q = q.join(Category, isouter=True).filter(
            or_(
                Category.slug == category,
                Category.name.ilike(f"%{category}%"),
                Product.tags.contains(category) if hasattr(Product.tags, 'contains') else True,
            )
        )

    # Text search
    search_terms = query.lower().replace("best", "").replace("under", "").replace("for", "").strip()
    if search_terms:
        q = q.filter(
            or_(
                Product.name.ilike(f"%{search_terms}%"),
                Product.description.ilike(f"%{search_terms}%"),
            )
        )

    # Budget filter
    if budget:
        q = q.filter(Product.current_best_price <= budget)

    # Get products
    products = (
        q.options(joinedload(Product.brand), joinedload(Product.category))
        .limit(50)
        .all()
    )

    # Score and rank products
    scored = [(p, score_product(p, query, budget)) for p in products]
    scored.sort(key=lambda x: x[1], reverse=True)
    top_products = scored[:5]

    # Generate recommendations
    recommendations = []
    for rank, (product, score) in enumerate(top_products, 1):
        pros, cons = generate_pros_cons(product)
        reasoning = generate_product_reasoning(product, rank, budget)

        recommendations.append(AIRecommendation(
            product=ProductResponse.model_validate(product),
            score=score,
            reasoning=reasoning,
            pros=pros,
            cons=cons,
            best_deal_platform=product.current_best_platform,
            best_deal_price=product.current_best_price,
        ))

    # Generate summary
    if recommendations:
        top = recommendations[0]
        summary = (
            f"Based on your query '{query}', I recommend **{top.product.name}** as the top choice "
            f"with a score of {top.score}/100. "
        )
        if budget:
            summary += f"All recommendations are within your ${budget:.0f} budget. "
        summary += f"I found {len(recommendations)} strong matches for you."
    else:
        summary = f"I couldn't find specific matches for '{query}'. Try broadening your search or adjusting your budget."

    return AIRecommendResponse(
        query=query,
        recommendations=recommendations,
        summary=summary,
    )


@router.post("/summary")
async def generate_comparison_summary(
    request: AISummaryRequest,
    db: Session = Depends(get_db),
):
    """Generate an AI-powered product comparison summary."""
    products = (
        db.query(Product)
        .filter(Product.id.in_(request.product_ids))
        .options(joinedload(Product.brand))
        .all()
    )

    if len(products) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 products")

    names = [p.name for p in products]
    summary_lines = [
        f"# {' vs '.join(names)}",
        "",
        "## Quick Verdict",
    ]

    # Find best by rating
    best_rated = max(products, key=lambda p: p.average_rating or 0)
    cheapest = min(products, key=lambda p: p.current_best_price or float('inf'))
    most_reviewed = max(products, key=lambda p: p.total_reviews or 0)

    if best_rated.average_rating:
        summary_lines.append(f"- **Best Rated**: {best_rated.name} ({best_rated.average_rating:.1f}/5)")
    if cheapest.current_best_price:
        summary_lines.append(f"- **Best Price**: {cheapest.name} (${cheapest.current_best_price:.2f})")
    if most_reviewed.total_reviews:
        summary_lines.append(f"- **Most Popular**: {most_reviewed.name} ({most_reviewed.total_reviews} reviews)")

    summary_lines.extend([
        "",
        "## Recommendation",
        f"For most users, **{best_rated.name}** offers the best overall experience. "
        f"If budget is a priority, **{cheapest.name}** provides better value for money.",
    ])

    return {"summary": "\n".join(summary_lines), "products": names}


@router.post("/cart-optimizer", response_model=CartOptimizerResponse)
async def optimize_cart(
    request: CartOptimizerRequest,
    db: Session = Depends(get_db),
):
    """Optimize a cart of items to find the best platform for each."""
    results = []
    total_cost = 0
    total_savings = 0

    for item in request.items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .options(joinedload(Product.brand), joinedload(Product.category))
            .first()
        )

        if not product:
            continue

        # Get prices across platforms
        prices = (
            db.query(Price)
            .filter(Price.product_id == item.product_id, Price.is_available == True)
            .order_by(Price.price.asc())
            .all()
        )

        if prices:
            best_price = prices[0]
            worst_price = prices[-1]
            savings = (worst_price.price - best_price.price) * item.quantity

            results.append(CartOptimizerResult(
                product=ProductResponse.model_validate(product),
                best_platform=best_price.platform,
                best_price=best_price.price * item.quantity,
                savings=round(savings, 2),
            ))

            total_cost += best_price.price * item.quantity
            total_savings += savings
        else:
            results.append(CartOptimizerResult(
                product=ProductResponse.model_validate(product),
                best_platform="N/A",
                best_price=product.current_best_price or 0,
                savings=0,
            ))
            total_cost += product.current_best_price or 0

    # Generate summary
    if results:
        summary = (
            f"Optimized {len(results)} items across platforms. "
            f"Total cost: ${total_cost:.2f}. "
            f"Total savings: ${total_savings:.2f} compared to buying everything at the highest price."
        )
    else:
        summary = "No items found for optimization."

    return CartOptimizerResponse(
        items=results,
        total_cost=round(total_cost, 2),
        total_savings=round(total_savings, 2),
        optimization_summary=summary,
    )
