"""
Brand Battle — Notification Platform Pydantic Schemas
Request and response schemas for notification feed, preferences, feedback, and digests.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NotificationPreferenceSchema(BaseModel):
    enable_in_app: bool = True
    enable_email: bool = True
    enable_push: bool = True
    enable_daily_digest: bool = True
    digest_frequency: str = "daily"
    quiet_hours_start: int = 22
    quiet_hours_end: int = 7
    max_daily_notifications: int = 3
    preferred_categories: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None


class NotificationItemSchema(BaseModel):
    id: int
    notification_type: str
    title: str
    body: str
    product_id: Optional[int] = None
    channel: str
    relevance_score: float
    is_read: bool
    delivered_at: datetime


class DailyDigestSchema(BaseModel):
    headline: str
    summary_text: str
    deal_count: int
    total_savings_inr: float
    items: List[Dict[str, Any]]
    created_at: datetime


class NotificationFeedbackSchema(BaseModel):
    notification_id: int
    is_helpful: bool
    feedback_text: Optional[str] = None


class HappinessMetricSchema(BaseModel):
    happiness_index_pct: float
    total_feedback_received: int
    helpful_votes: int
    unhelpful_votes: int
    average_fatigue_score: float
