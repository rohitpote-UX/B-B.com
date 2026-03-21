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


# ─── Enums ───────────────────────────────────────────────────────────

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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")
    affiliate_links = relationship("AffiliateLink", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_product_search", "name", "is_active"),
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
