"""
Brand Battle - Database Models
Complete schema with 14+ tables covering users, products, brands,
prices, reviews, comparisons, alerts, notifications, and affiliates.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import uuid


# ─── Enums ───────────────────────────────────────────────────────────


class VerificationStatus(str, enum.Enum):
    VERIFIED = "verified"
    RECENTLY_VERIFIED = "recently_verified"
    STALE = "stale"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"
    FAILED = "failed_verification"


class ScrapeStatus(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    NO_DATA = "no_data"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    PARSER_ERROR = "parser_error"
    PRICE_CHANGED = "price_changed"
    PRODUCT_NOT_FOUND = "product_not_found"
    IMAGE_NOT_FOUND = "image_not_found"
    RATE_LIMITED = "rate_limited"
    SOURCE_UNAVAILABLE = "source_unavailable"


class AnomalyType(str, enum.Enum):
    SUDDEN_DROP = "sudden_drop"
    SUDDEN_SPIKE = "sudden_spike"
    IMPOSSIBLE_PRICE = "impossible_price"
    VARIANT_MISMATCH = "variant_mismatch"
    CURRENCY_ERROR = "currency_error"


class AnomalyResolution(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CORRECTED = "corrected"

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    PAUSED = "paused"


class NotificationType(str, enum.Enum):
    PRICE_DROP = "price_drop"
    NEW_DEAL = "new_deal"
    BETTER_DEAL = "better_deal"
    COMPARISON_UPDATE = "comparison_update"
    SYSTEM = "system"


class Platform(str, enum.Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    MYNTRA = "myntra"
    AJIO = "ajio"
    CROMA = "croma"
    RELIANCE_DIGITAL = "reliance_digital"
    BRAND_STORE = "brand_store"
    OTHER = "other"


class DealStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    UPCOMING = "upcoming"


class RelationshipType(str, enum.Enum):
    SAME_PRODUCT = "same_product"
    ALTERNATIVE = "alternative"
    NEWER_VERSION = "newer_version"
    OLDER_VERSION = "older_version"
    PREMIUM_ALTERNATIVE = "premium_alternative"
    BUDGET_ALTERNATIVE = "budget_alternative"
    SIMILAR_STYLE = "similar_style"
    SAME_BRAND = "same_brand"
    FREQUENTLY_COMPARED = "frequently_compared"
    COMPATIBLE = "compatible"
    ACCESSORY = "accessory"
    REPLACEMENT = "replacement"
    COMPLEMENTARY = "complementary"


class OfferStatus(str, enum.Enum):
    ACTIVE = "active"
    UNAVAILABLE = "unavailable"
    DISCONTINUED = "discontinued"
    PRICE_ERROR = "price_error"


class AttributeType(str, enum.Enum):
    TEXT = "text"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    ENUM = "enum"
    COLOR = "color"
    DIMENSION = "dimension"


class ProductLifecycleState(str, enum.Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    MERGED = "merged"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


class ReviewQueueStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    SPLIT = "split"


class AuditEventType(str, enum.Enum):
    MASTER_CREATED = "master_created"
    MASTER_UPDATED = "master_updated"
    MASTER_MERGED = "master_merged"
    MASTER_ARCHIVED = "master_archived"
    MASTER_ROLLBACK = "master_rollback"
    OFFER_LINKED = "offer_linked"
    OFFER_UPDATED = "offer_updated"
    RELATIONSHIP_CREATED = "relationship_created"
    RELATIONSHIP_REMOVED = "relationship_removed"
    REVIEW_TRIGGERED = "review_triggered"
    REVIEW_DECIDED = "review_decided"
    CACHE_INVALIDATED = "cache_invalidated"


# ─── Users ───────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    preferences = Column(JSON, nullable=True)  # {budget_range, categories, brands}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    saved_comparisons = relationship("SavedComparison", back_populates="user", cascade="all, delete-orphan")


# ─── Brands ──────────────────────────────────────────────────────────

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    trust_score = Column(Float, default=0.0)  # 0-10 brand reputation score
    customer_satisfaction = Column(Float, default=0.0)
    return_rate = Column(Float, default=0.0)
    review_sentiment = Column(Float, default=0.0)
    durability_score = Column(Float, default=0.0)
    category = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="brand")


# ─── Categories ──────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    icon = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Self-referential relationship for subcategories
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


# ─── Products ────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    images = Column(JSON, nullable=True)  # Array of image URLs
    specifications = Column(JSON, nullable=True)  # {key: value} pairs
    features = Column(JSON, nullable=True)  # Array of feature strings
    tags = Column(JSON, nullable=True)  # Array of tags
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    lowest_price = Column(Float, nullable=True)
    highest_price = Column(Float, nullable=True)
    current_best_price = Column(Float, nullable=True)
    current_best_platform = Column(String(50), nullable=True)
    deal_score = Column(Float, nullable=True)  # AI-calculated deal quality 0-100
    ai_summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    compare_count = Column(Integer, default=0)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Data Trust Hardening — product-level verification state
    data_quality_score = Column(Float, default=0.0)  # 0-100 internal score
    price_verified_at = Column(DateTime(timezone=True), nullable=True)
    image_verified_at = Column(DateTime(timezone=True), nullable=True)
    price_verification_status = Column(String(30), default=VerificationStatus.UNVERIFIED.value)
    data_source = Column(String(50), default="seed")  # seed, pipeline, api, manual

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")
    affiliate_links = relationship("AffiliateLink", back_populates="product", cascade="all, delete-orphan")
    master_product = relationship("MasterProduct", back_populates="products")

    __table_args__ = (
        Index("idx_product_search", "name", "is_active"),
        Index("idx_product_category_brand", "category_id", "brand_id", "is_active"),
        Index("idx_product_price_score", "current_best_price", "deal_score", "average_rating"),
    )


# ─── Prices (Current prices across platforms) ───────────────────────

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)  # Before discount
    discount_percentage = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    url = Column(String(1000), nullable=True)
    is_available = Column(Boolean, default=True)
    delivery_days = Column(Integer, nullable=True)
    delivery_cost = Column(Float, default=0.0)
    seller_name = Column(String(255), nullable=True)
    seller_rating = Column(Float, nullable=True)
    is_best_deal = Column(Boolean, default=False)
    last_checked = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Data Trust Hardening — verification provenance
    verification_status = Column(String(30), default=VerificationStatus.UNVERIFIED.value)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    source_method = Column(String(50), nullable=True)  # api, scraper, feed, manual, seed
    confidence_score = Column(Float, default=0.0)  # 0.0 - 1.0
    parser_version = Column(String(50), nullable=True)
    failure_reason = Column(String(500), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("product_id", "platform", name="uq_product_platform"),
        Index("idx_price_lookup", "product_id", "platform", "is_available"),
    )


# ─── Price History ───────────────────────────────────────────────────

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="price_history")

    __table_args__ = (
        Index("idx_price_history_lookup", "product_id", "platform", "recorded_at"),
    )


# ─── Reviews ─────────────────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    source = Column(String(100), nullable=True)  # "amazon", "youtube", "reddit", etc.
    reviewer_name = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)  # Array of pros
    cons = Column(JSON, nullable=True)  # Array of cons
    is_verified = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    review_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")


# ─── Comparisons ─────────────────────────────────────────────────────

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    product_ids = Column(JSON, nullable=False)  # Array of product IDs
    winner_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    ai_summary = Column(Text, nullable=True)
    feature_scores = Column(JSON, nullable=True)  # {feature: {product_id: score}}
    view_count = Column(Integer, default=0)
    is_trending = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SavedComparison(Base):
    __tablename__ = "saved_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_comparisons")


# ─── Votes ───────────────────────────────────────────────────────────

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "comparison_id", name="uq_user_comparison_vote"),
    )


# ─── Price Alerts ────────────────────────────────────────────────────

class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    platform = Column(String(50), nullable=True)  # None = any platform
    status = Column(String(20), default=AlertStatus.ACTIVE.value)
    notify_email = Column(Boolean, default=True)
    notify_push = Column(Boolean, default=True)
    notify_browser = Column(Boolean, default=True)
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")

    __table_args__ = (
        Index("idx_alert_eval", "user_id", "status", "target_price"),
    )


# ─── Notifications ───────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # {product_id, comparison_id, url, etc.}
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")


# ─── Affiliate Links ────────────────────────────────────────────────

class AffiliateLink(Base):
    __tablename__ = "affiliate_links"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    affiliate_url = Column(String(1000), nullable=False)
    commission_rate = Column(Float, nullable=True)
    click_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="affiliate_links")


# ─── Search History ──────────────────────────────────────────────────

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(String(500), nullable=False)
    filters = Column(JSON, nullable=True)
    results_count = Column(Integer, default=0)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="search_history")

    __table_args__ = (
        Index("idx_search_history_query", "query"),
    )


# ─── Deals ───────────────────────────────────────────────────────────

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    deal_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    deal_score = Column(Float, nullable=True)  # AI quality score 0-100
    is_fake_discount = Column(Boolean, default=False)
    real_market_price = Column(Float, nullable=True)
    url = Column(String(1000), nullable=True)
    coupon_code = Column(String(100), nullable=True)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default=DealStatus.ACTIVE.value)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_deal_active", "status", "expires_at"),
        Index("idx_deal_platform_score", "platform", "deal_score", "discount_percentage"),
    )


# ─── Analytics ───────────────────────────────────────────────────────

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)  # page_view, search, click, compare, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, nullable=True)
    data = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_analytics_type_date", "event_type", "created_at"),
    )


# ─── Knowledge Graph: Master Products ────────────────────────────────

class MasterProduct(Base):
    """Canonical product identity — the single source of truth for a real-world product."""
    __tablename__ = "master_products"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    canonical_name = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    # Product identity fields
    gender = Column(String(20), nullable=True)  # men, women, unisex, kids
    color_family = Column(String(50), nullable=True)  # normalized: blue, red, black, etc.
    material = Column(String(100), nullable=True)  # normalized: leather, cotton, polyester, etc.
    product_type = Column(String(100), nullable=True)  # sneakers, laptop, headphones, etc.
    model_series = Column(String(200), nullable=True)  # Air Force, Galaxy S, MacBook Pro, etc.
    model_name = Column(String(200), nullable=True)  # Air Force 1 '07, Galaxy S26 Ultra, etc.
    variant = Column(String(200), nullable=True)  # 256GB White, Slim Fit, etc.
    release_year = Column(Integer, nullable=True)
    global_sku = Column(String(100), nullable=True, index=True)

    # Aggregated data (computed from offers)
    specifications = Column(JSON, nullable=True)  # Merged specifications from all offers
    features = Column(JSON, nullable=True)  # Merged feature list
    images = Column(JSON, nullable=True)  # Aggregated image URLs from all sources
    primary_image_url = Column(String(500), nullable=True)

    # Computed metrics
    offer_count = Column(Integer, default=0)
    lowest_price = Column(Float, nullable=True)
    highest_price = Column(Float, nullable=True)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)  # 0.0 - 1.0 matching confidence

    # Enterprise Hardening fields
    public_id = Column(String(50), unique=True, nullable=True, index=True)  # e.g., BB-PRD-0000000001
    version = Column(Integer, default=1, nullable=False)  # Optimistic concurrency lock
    status = Column(String(20), default=ProductLifecycleState.ACTIVE.value, index=True)
    completeness_score = Column(Float, default=0.0)  # 0.0 - 100.0
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", foreign_keys=[brand_id])
    category = relationship("Category", foreign_keys=[category_id])
    subcategory = relationship("Category", foreign_keys=[subcategory_id])
    products = relationship("Product", back_populates="master_product")
    offers = relationship("MarketplaceOffer", back_populates="master_product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="master_product", cascade="all, delete-orphan")
    kg_images = relationship("ProductImage", back_populates="master_product", cascade="all, delete-orphan")
    tags = relationship("ProductTag", back_populates="master_product", cascade="all, delete-orphan")
    search_metadata = relationship("SearchMetadata", back_populates="master_product", uselist=False, cascade="all, delete-orphan")
    versions = relationship("MasterProductVersion", back_populates="master_product", cascade="all, delete-orphan")
    confidence_history = relationship("MatchingConfidenceHistory", back_populates="master_product", cascade="all, delete-orphan")
    review_items = relationship("ReviewQueueItem", back_populates="master_product", cascade="all, delete-orphan")

    # Relationship edges (outgoing)
    outgoing_relationships = relationship(
        "ProductRelationship",
        foreign_keys="ProductRelationship.source_master_id",
        back_populates="source_master",
        cascade="all, delete-orphan",
    )
    incoming_relationships = relationship(
        "ProductRelationship",
        foreign_keys="ProductRelationship.target_master_id",
        back_populates="target_master",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_master_brand_cat", "brand_id", "category_id", "is_active"),
        Index("idx_master_model", "model_series", "model_name"),
        Index("idx_master_search", "canonical_name", "product_type", "is_active"),
    )


# ─── Knowledge Graph: Marketplace Offers ─────────────────────────────

class MarketplaceOffer(Base):
    """A single marketplace listing linked to a canonical MasterProduct."""
    __tablename__ = "marketplace_offers"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    marketplace = Column(String(50), nullable=False, index=True)
    marketplace_product_id = Column(String(200), nullable=True)  # External ID on marketplace
    title = Column(String(500), nullable=False)  # Original marketplace title
    url = Column(String(1000), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Pricing
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")

    # Seller
    seller_name = Column(String(255), nullable=True)
    seller_rating = Column(Float, nullable=True)

    # Availability
    stock_status = Column(String(50), default="in_stock")  # in_stock, low_stock, out_of_stock
    is_available = Column(Boolean, default=True)
    delivery_time = Column(String(100), nullable=True)  # "2-3 days", "Same day", etc.
    shipping_cost = Column(Float, default=0.0)
    warranty = Column(String(200), nullable=True)

    # Reviews (marketplace-specific)
    review_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)

    # Status & Freshness Tracking
    status = Column(String(20), default=OfferStatus.ACTIVE.value, index=True)
    match_confidence = Column(Float, default=0.0)  # Confidence this offer matches the master
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    last_crawl_time = Column(DateTime(timezone=True), nullable=True)
    last_price_update = Column(DateTime(timezone=True), nullable=True)
    last_availability_check = Column(DateTime(timezone=True), nullable=True)
    freshness_score = Column(Float, default=1.0)  # 0.0 - 1.0
    update_frequency_hours = Column(Float, default=24.0)
    data_source_reliability = Column(Float, default=1.0)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Data Trust Hardening — offer-level verification state
    verification_status = Column(String(30), default=VerificationStatus.UNVERIFIED.value)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    source_method = Column(String(50), nullable=True)  # api, scraper, feed, manual
    confidence_score = Column(Float, default=0.0)  # 0.0 - 1.0
    parser_version = Column(String(50), nullable=True)
    failure_reason = Column(String(500), nullable=True)
    shipping_cost_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="offers")

    __table_args__ = (
        UniqueConstraint("master_product_id", "marketplace", "url", name="uq_offer_marketplace_url"),
        Index("idx_offer_marketplace", "marketplace", "is_available"),
        Index("idx_offer_price", "master_product_id", "price", "is_available"),
    )


# ─── Knowledge Graph: Product Relationships ──────────────────────────

class ProductRelationship(Base):
    """Typed, weighted edge between two MasterProducts in the knowledge graph."""
    __tablename__ = "product_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_master_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    target_master_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, default=1.0)  # 0.0 - 1.0
    weight = Column(Float, default=1.0)  # Signal-weighted score for graph traversal
    discovery_method = Column(String(50), default="auto")  # auto, ai_semantic, manual
    creation_source = Column(String(50), default="system")
    signal_breakdown = Column(JSON, nullable=True)  # {"brand": 1.0, "category": 1.0, "price": 0.8}
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_bidirectional = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)  # Extra context (e.g., {"reason": "same brand + category"})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_master = relationship("MasterProduct", foreign_keys=[source_master_id], back_populates="outgoing_relationships")
    target_master = relationship("MasterProduct", foreign_keys=[target_master_id], back_populates="incoming_relationships")

    __table_args__ = (
        UniqueConstraint("source_master_id", "target_master_id", "relationship_type", name="uq_product_relationship"),
        Index("idx_rel_type", "relationship_type", "confidence"),
    )


# ─── Knowledge Graph: Product Attributes ─────────────────────────────

class ProductAttribute(Base):
    """Structured, searchable product attributes for a MasterProduct."""
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    attribute_name = Column(String(100), nullable=False, index=True)
    attribute_value = Column(String(500), nullable=False)
    attribute_type = Column(String(20), default=AttributeType.TEXT.value)
    unit = Column(String(50), nullable=True)  # "GB", "mm", "g", etc.
    is_searchable = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="attributes")

    __table_args__ = (
        UniqueConstraint("master_product_id", "attribute_name", name="uq_product_attribute"),
        Index("idx_attr_search", "attribute_name", "attribute_value", "is_searchable"),
    )


# ─── Knowledge Graph: Product Images ─────────────────────────────────

class ProductImage(Base):
    """Multi-source image collection for a MasterProduct."""
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    url = Column(String(1000), nullable=False)
    source_marketplace = Column(String(50), nullable=True)
    alt_text = Column(String(500), nullable=True)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Data Trust Hardening — image verification
    http_status = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    image_hash = Column(String(64), nullable=True)
    verification_status = Column(String(30), default=VerificationStatus.UNVERIFIED.value)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(String(500), nullable=True)

    # Relationships
    master_product = relationship("MasterProduct", back_populates="kg_images")


# ─── Knowledge Graph: Product Tags ───────────────────────────────────

class ProductTag(Base):
    """Searchable, categorized tags for a MasterProduct."""
    __tablename__ = "product_tags"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    tag = Column(String(100), nullable=False, index=True)
    tag_type = Column(String(50), nullable=True)  # category, style, occasion, material, season, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("master_product_id", "tag", name="uq_product_tag"),
        Index("idx_tag_type", "tag_type", "tag"),
    )


# ─── Knowledge Graph: Search Metadata ────────────────────────────────

class SearchMetadata(Base):
    """Pre-computed search optimization data for a MasterProduct."""
    __tablename__ = "search_metadata"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, unique=True)
    search_vector = Column(Text, nullable=True)  # Concatenated searchable text
    synonyms = Column(JSON, nullable=True)  # ["sneakers", "trainers", "kicks"]
    boost_score = Column(Float, default=1.0)  # Search ranking boost
    trending_score = Column(Float, default=0.0)  # Computed from views/comparisons
    popularity_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=1.0)
    quality_score = Column(Float, default=1.0)
    completeness_score = Column(Float, default=0.0)
    trend_score = Column(Float, default=0.0)
    click_score = Column(Float, default=0.0)
    comparison_score = Column(Float, default=0.0)
    recommendation_score = Column(Float, default=0.0)
    ai_confidence = Column(Float, default=1.0)
    update_frequency = Column(String(50), default="daily")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="search_metadata")


# ─── Knowledge Graph: Graph Metrics ──────────────────────────────────

class GraphMetrics(Base):
    """Singleton row tracking overall Knowledge Graph health and statistics."""
    __tablename__ = "graph_metrics"

    id = Column(Integer, primary_key=True, index=True)
    total_masters = Column(Integer, default=0)
    total_offers = Column(Integer, default=0)
    total_relationships = Column(Integer, default=0)
    total_attributes = Column(Integer, default=0)
    orphan_products = Column(Integer, default=0)  # Products without a master
    avg_confidence = Column(Float, default=0.0)
    avg_offers_per_master = Column(Float, default=0.0)
    duplicate_detection_rate = Column(Float, default=0.0)
    last_computed = Column(DateTime(timezone=True), server_default=func.now())


# ─── Knowledge Graph: Enterprise Hardening Tables ─────────────────────

class MasterProductVersion(Base):
    """Immutable historical version snapshot for a MasterProduct."""
    __tablename__ = "master_product_versions"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    canonical_name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    primary_image_url = Column(String(500), nullable=True)
    category_id = Column(Integer, nullable=True)
    brand_id = Column(Integer, nullable=True)
    specifications = Column(JSON, nullable=True)
    features = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    attributes_json = Column(JSON, nullable=True)
    ai_summary = Column(Text, nullable=True)
    search_metadata_json = Column(JSON, nullable=True)
    tags_json = Column(JSON, nullable=True)
    changed_fields = Column(JSON, nullable=True)  # Array of field names modified
    source_of_change = Column(String(100), default="system")  # pipeline, admin_api, merge, rollback
    updated_by = Column(String(100), default="system")
    change_reason = Column(String(500), nullable=True)
    previous_version_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("master_product_id", "version_number", name="uq_master_version"),
        Index("idx_version_lookup", "master_product_id", "version_number"),
    )


class MatchingConfidenceHistory(Base):
    """Historical audit log of AI product matching decisions and confidence scores."""
    __tablename__ = "matching_confidence_history"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False, index=True)
    offer_id = Column(Integer, nullable=True)
    matching_score = Column(Float, nullable=False)
    algorithm_version = Column(String(50), default="v2.0_multi_signal")
    model_version = Column(String(50), default="gemini-flash-kg")
    decision_type = Column(String(50), nullable=False)  # auto_matched, auto_created, manual_review, merged
    matching_signals = Column(JSON, nullable=True)  # Signal breakdown dict
    reviewer_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="confidence_history")

    __table_args__ = (
        Index("idx_conf_hist_master", "master_product_id", "created_at"),
    )


class GraphAuditEvent(Base):
    """Immutable audit event log for every mutation on the Product Knowledge Graph."""
    __tablename__ = "graph_audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    correlation_id = Column(String(36), nullable=True, index=True)
    actor = Column(String(100), default="system")  # system, admin_user, background_job
    entity_type = Column(String(100), nullable=False, index=True)  # master_product, offer, relationship, etc.
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # create, update, merge, archive, delete
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id", "created_at"),
        Index("idx_audit_action", "action", "created_at"),
    )


class ReviewQueueItem(Base):
    """Intelligent human-in-the-loop review queue item for low-confidence or conflicting matches."""
    __tablename__ = "review_queue_items"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=True, index=True)
    offer_id = Column(Integer, nullable=True)
    trigger_reason = Column(String(255), nullable=False)  # low_confidence, uncertain_duplicate, brand_mismatch
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default=ReviewQueueStatus.PENDING.value, index=True)
    confidence_score = Column(Float, default=0.0)
    metadata_json = Column(JSON, nullable=True)  # Raw payload and candidate info
    reviewer_id = Column(Integer, nullable=True)
    decision_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    master_product = relationship("MasterProduct", back_populates="review_items")

    __table_args__ = (
        Index("idx_review_queue_status", "status", "priority", "created_at"),
    )


class HistoricalGraphSnapshot(Base):
    """Historical periodic snapshot of overall Knowledge Graph health and growth metrics."""
    __tablename__ = "historical_graph_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    snapshot_type = Column(String(20), default="daily")  # daily, weekly, monthly
    total_masters = Column(Integer, default=0)
    total_offers = Column(Integer, default=0)
    total_relationships = Column(Integer, default=0)
    total_attributes = Column(Integer, default=0)
    duplicate_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    avg_completeness = Column(Float, default=0.0)
    avg_offer_freshness = Column(Float, default=0.0)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_snapshot_date_type", "snapshot_type", "snapshot_date"),
    )


# ─── Matching Engine Phase 2 Tables ──────────────────────────────────

class MatchingHistoryLog(Base):
    """Immutable audit trail log for Hybrid AI Product Matching Engine decisions."""
    __tablename__ = "matching_history_logs"

    id = Column(Integer, primary_key=True, index=True)
    listing_title = Column(String(500), nullable=False, index=True)
    marketplace = Column(String(50), nullable=False)
    candidates_evaluated_count = Column(Integer, default=0)
    winning_candidate_id = Column(Integer, ForeignKey("master_products.id"), nullable=True, index=True)
    decision = Column(String(50), nullable=False, index=True)  # auto_matched, create_new, route_review, merged
    confidence_score = Column(Float, nullable=False)
    signal_breakdown_json = Column(JSON, nullable=True)
    explainability_json = Column(JSON, nullable=True)
    embedding_model_version = Column(String(50), default="tf_idf_v1_ngram")
    algorithm_version = Column(String(50), default="v2.5_hybrid_ensemble")
    execution_time_ms = Column(Float, default=0.0)
    fallback_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    winning_candidate = relationship("MasterProduct", foreign_keys=[winning_candidate_id])

    __table_args__ = (
        Index("idx_match_history_decision", "decision", "confidence_score"),
    )


class TrainingFeedbackRecord(Base):
    """Human-in-the-loop reviewer feedback dataset for continuous learning."""
    __tablename__ = "training_feedback_records"

    id = Column(Integer, primary_key=True, index=True)
    master_product_id = Column(Integer, ForeignKey("master_products.id"), nullable=True, index=True)
    offer_id = Column(Integer, nullable=True)
    candidate_master_id = Column(Integer, nullable=True)
    feedback_type = Column(String(50), nullable=False, index=True)  # approved_match, rejected_match, false_positive, false_negative, manual_correction
    signal_snapshot_json = Column(JSON, nullable=True)
    reviewer_id = Column(Integer, nullable=True)
    decision_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_feedback_type", "feedback_type", "created_at"),
    )


# ─── Data Trust Hardening: Operational Tables ────────────────────────

class ScraperHealthLog(Base):
    """Immutable log of every scraper execution for monitoring and Admin Console."""
    __tablename__ = "scraper_health_logs"

    id = Column(Integer, primary_key=True, index=True)
    marketplace = Column(String(50), nullable=False, index=True)
    parser_version = Column(String(50), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), nullable=False)  # ScrapeStatus enum values
    products_found = Column(Integer, default=0)
    prices_extracted = Column(Integer, default=0)
    images_extracted = Column(Integer, default=0)
    failures = Column(Integer, default=0)
    failure_reason = Column(String(500), nullable=True)
    http_status = Column(Integer, nullable=True)
    duration_ms = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_scraper_health_marketplace", "marketplace", "status", "started_at"),
    )


class PriceAnomalyLog(Base):
    """Tracks price anomalies that require secondary verification before acceptance."""
    __tablename__ = "price_anomaly_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    offer_id = Column(Integer, nullable=True)
    marketplace = Column(String(50), nullable=False)
    previous_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    absolute_difference = Column(Float, nullable=False)
    percentage_difference = Column(Float, nullable=False)
    anomaly_type = Column(String(50), nullable=False)  # AnomalyType enum values
    resolution = Column(String(30), default=AnomalyResolution.PENDING.value)
    resolved_by = Column(String(100), nullable=True)
    resolution_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_anomaly_product", "product_id", "resolution", "created_at"),
    )


class DataFreshnessConfig(Base):
    """Configuration-driven TTL values for price/image freshness tiers."""
    __tablename__ = "data_freshness_config"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Integer, nullable=False)  # seconds
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
