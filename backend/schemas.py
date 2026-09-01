"""
Brand Battle - Pydantic Schemas
Request/Response models for all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Auth Schemas ────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# ─── Brand Schemas ───────────────────────────────────────────────────

class BrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    trust_score: float
    customer_satisfaction: float
    return_rate: float
    review_sentiment: float
    durability_score: float
    category: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True


# ─── Category Schemas ────────────────────────────────────────────────

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


# ─── Product Schemas ─────────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ProductCreate(ProductBase):
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    images: Optional[List[str]] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    average_rating: float
    total_reviews: int
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    current_best_price: Optional[float] = None
    current_best_platform: Optional[str] = None
    deal_score: Optional[float] = None
    ai_summary: Optional[str] = None
    view_count: int
    compare_count: int
    brand: Optional[BrandResponse] = None
    category: Optional[CategoryResponse] = None
    created_at: Optional[datetime] = None
    # Data Trust Hardening — verification metadata
    price_verified_at: Optional[datetime] = None
    price_verification_status: Optional[str] = None
    data_quality_score: Optional[float] = None
    data_source: Optional[str] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductSearchQuery(BaseModel):
    query: str = ""
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    sort_by: str = "relevance"  # relevance, price_asc, price_desc, rating, newest
    page: int = 1
    page_size: int = 20


# ─── Price Schemas ───────────────────────────────────────────────────

class PriceResponse(BaseModel):
    id: int
    product_id: int
    platform: str
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    currency: str
    url: Optional[str] = None
    is_available: bool
    delivery_days: Optional[int] = None
    delivery_cost: float
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    is_best_deal: bool
    last_checked: Optional[datetime] = None
    # Data Trust Hardening — verification provenance
    verification_status: Optional[str] = None
    verified_at: Optional[datetime] = None
    confidence_score: Optional[float] = None
    source_method: Optional[str] = None

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    platform: str
    price: float
    currency: str
    recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PriceHistoryListResponse(BaseModel):
    history: List[PriceHistoryResponse]
    lowest_price: float
    highest_price: float
    average_price: float
    best_time_to_buy: Optional[str] = None


# ─── Review Schemas ──────────────────────────────────────────────────

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    platform: str
    source: Optional[str] = None
    reviewer_name: Optional[str] = None
    rating: Optional[float] = None
    title: Optional[str] = None
    content: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    is_verified: bool
    helpful_count: int
    sentiment_score: Optional[float] = None
    review_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewSummaryResponse(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]  # {"5": 120, "4": 80, ...}
    top_pros: List[str]
    top_cons: List[str]
    common_complaints: List[str]
    ai_summary: str
    reviews: List[ReviewResponse]


# ─── Comparison Schemas ──────────────────────────────────────────────

class ComparisonCreate(BaseModel):
    product_ids: List[int] = Field(..., min_length=2, max_length=5)


class ComparisonResponse(BaseModel):
    id: int
    slug: str
    title: str
    product_ids: List[int]
    winner_id: Optional[int] = None
    ai_summary: Optional[str] = None
    feature_scores: Optional[Dict[str, Any]] = None
    view_count: int
    is_trending: bool
    products: Optional[List[ProductResponse]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComparisonDetailResponse(BaseModel):
    comparison: ComparisonResponse
    products: List[ProductResponse]
    prices: Dict[int, List[PriceResponse]]  # product_id -> prices
    feature_comparison: Dict[str, Dict[int, Any]]  # feature -> {product_id: value}
    winners: Dict[str, int]  # category -> winning product_id
    ai_summary: str
    vote_results: Optional[Dict[int, int]] = None  # product_id -> vote count


# ─── Deal Schemas ────────────────────────────────────────────────────

class DealResponse(BaseModel):
    id: int
    product_id: int
    platform: str
    title: str
    description: Optional[str] = None
    deal_price: float
    original_price: float
    discount_percentage: float
    deal_score: Optional[float] = None
    is_fake_discount: bool
    real_market_price: Optional[float] = None
    url: Optional[str] = None
    coupon_code: Optional[str] = None
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str
    view_count: int
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class DealListResponse(BaseModel):
    deals: List[DealResponse]
    total: int
    page: int
    page_size: int


# ─── Alert Schemas ───────────────────────────────────────────────────

class AlertCreate(BaseModel):
    product_id: int
    target_price: float
    platform: Optional[str] = None
    notify_email: bool = True
    notify_push: bool = True
    notify_browser: bool = True


class AlertResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    target_price: float
    current_price: Optional[float] = None
    platform: Optional[str] = None
    status: str
    notify_email: bool
    notify_push: bool
    notify_browser: bool
    triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# ─── Notification Schemas ────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── AI Schemas ──────────────────────────────────────────────────────

class AIRecommendRequest(BaseModel):
    query: str
    budget: Optional[float] = None
    purpose: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class AIRecommendation(BaseModel):
    product: ProductResponse
    score: float
    reasoning: str
    pros: List[str]
    cons: List[str]
    best_deal_platform: Optional[str] = None
    best_deal_price: Optional[float] = None


class AIRecommendResponse(BaseModel):
    query: str
    recommendations: List[AIRecommendation]
    summary: str


class AISummaryRequest(BaseModel):
    product_ids: List[int]
    context: Optional[str] = None


# ─── Cart Optimizer Schemas ──────────────────────────────────────────

class CartItem(BaseModel):
    product_id: int
    quantity: int = 1


class CartOptimizerRequest(BaseModel):
    items: List[CartItem]


class CartOptimizerResult(BaseModel):
    product: ProductResponse
    best_platform: str
    best_price: float
    savings: float


class CartOptimizerResponse(BaseModel):
    items: List[CartOptimizerResult]
    total_cost: float
    total_savings: float
    optimization_summary: str


# ─── Analytics Schemas ───────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_users: int
    total_products: int
    total_searches: int
    total_comparisons: int
    total_deals: int
    active_alerts: int
    top_searches: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    revenue: float


# ─── Vote Schemas ────────────────────────────────────────────────────

class VoteCreate(BaseModel):
    comparison_id: int
    product_id: int


class VoteResultResponse(BaseModel):
    comparison_id: int
    results: Dict[int, int]  # product_id -> vote count
    total_votes: int
    user_vote: Optional[int] = None  # product_id user voted for
