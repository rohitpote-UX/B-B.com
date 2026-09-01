"""
Brand Battle — Search Platform REST API Layer
FastAPI router mounted at /api/search/* exposing search, autocomplete, facets,
suggestions, feedback, history, metrics, and health endpoints.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from auth import get_current_user_optional
from models import User
from search_platform.search_service import search_service
from logging_config import logger

router = APIRouter(prefix="/api/search", tags=["Search"])


# ─── Request / Response Models ───────────────────────────────────────

class SearchFeedbackRequest(BaseModel):
    query: str
    product_id: int
    position: int
    session_id: Optional[str] = None


# ─── Endpoints ───────────────────────────────────────────────────────

@router.get("/query")
async def search_query(
    q: str = Query("", description="Search query string"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    sort_by: Optional[str] = Query(None, description="Sort order: relevance, price_asc, price_desc, rating, newest"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Full AI-powered search with intent understanding, hybrid retrieval,
    multi-signal ranking, explainability, and faceted results.
    """
    user_id = current_user.id if current_user else None

    # Build filters dict from query params
    filters = {}
    if brand:
        filters["brand"] = brand
    if category:
        filters["category"] = category
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    if min_rating is not None:
        filters["min_rating"] = min_rating
    if sort_by:
        filters["sort_by"] = sort_by

    result = search_service.search(
        query=q,
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        filters=filters if filters else None,
    )

    return {
        "success": True,
        "message": f"Found {result.get('total', 0)} results for '{q}'",
        "data": result,
    }


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query("", description="Autocomplete prefix"),
    limit: int = Query(10, ge=1, le=20, description="Max suggestions"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Sub-20ms autocomplete suggestions for products, brands, categories, and popular searches."""
    user_id = current_user.id if current_user else None

    result = search_service.autocomplete(
        prefix=q,
        db=db,
        user_id=user_id,
        limit=limit,
    )

    return {
        "success": True,
        "message": f"Generated {len(result.get('suggestions', []))} suggestions",
        "data": result,
    }


@router.get("/facets")
async def get_facets(
    q: str = Query("", description="Query for facet generation"),
    db: Session = Depends(get_db),
):
    """Generate dynamic faceted filters from the Product Knowledge Graph for a query."""
    result = search_service.get_facets(query=q, db=db)

    return {
        "success": True,
        "message": f"Generated {len(result.get('facets', []))} facets",
        "data": result,
    }


@router.get("/suggestions")
async def get_suggestions(
    db: Session = Depends(get_db),
):
    """Get popular and trending search suggestions."""
    result = search_service.get_suggestions(db=db)

    return {
        "success": True,
        "message": "Search suggestions retrieved",
        "data": result,
    }


@router.post("/feedback")
async def record_feedback(
    payload: SearchFeedbackRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Record search result click/interaction feedback for ranking optimization."""
    user_id = current_user.id if current_user else None

    result = search_service.record_feedback(
        query=payload.query,
        product_id=payload.product_id,
        position=payload.position,
        user_id=user_id,
        session_id=payload.session_id,
    )

    return {
        "success": result.get("success", False),
        "message": result.get("message", ""),
    }


@router.get("/history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get the authenticated user's search history."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = search_service.get_user_history(
        user_id=current_user.id, db=db, limit=limit
    )

    return {
        "success": True,
        "message": f"Retrieved {len(result.get('history', []))} history entries",
        "data": result,
    }


@router.get("/metrics")
async def get_metrics():
    """Search platform observability telemetry dashboard."""
    return {
        "success": True,
        "message": "Search metrics retrieved",
        "data": search_service.get_metrics(),
    }


@router.get("/health")
async def search_health():
    """Search platform health check."""
    return {
        "success": True,
        "message": "Search platform health status",
        "data": search_service.health_check(),
    }
