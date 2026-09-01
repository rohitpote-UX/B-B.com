"""
Brand Battle — 1. Universal Event Collection Schema
Standardized structured event schema supporting schema versioning and metadata payloads.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class UniversalEventPayload(BaseModel):
    """Standardized enterprise analytics event schema."""
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: Optional[int] = None
    session_id: str = "guest_session"
    device_type: str = "desktop"
    browser: str = "chrome"
    country: str = "IN"
    currency: str = "INR"
    event_category: str  # search, product, compare, rec, alert, notification, deal, wishlist
    event_type: str      # search_performed, product_viewed, item_compared, rec_clicked, alert_created
    metadata: Dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "v1.0"
