"""
Brand Battle — Analytics Platform Pydantic Schemas
Request and response schemas for event ingestion, dashboard metrics, AI insights, and ops health.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EventIngestSchema(BaseModel):
    event_type: str
    event_category: str
    user_id: Optional[int] = None
    session_id: Optional[str] = "guest_session"
    device_type: Optional[str] = "desktop"
    browser: Optional[str] = "chrome"
    country: Optional[str] = "IN"
    currency: Optional[str] = "INR"
    payload: Optional[Dict[str, Any]] = None


class BatchEventIngestSchema(BaseModel):
    events: List[EventIngestSchema]


class ExecutiveDashboardSchema(BaseModel):
    dau: int
    mau: int
    retention_rate_pct: float
    recommendation_ctr_pct: float
    search_success_pct: float
    price_forecast_accuracy_pct: float
    notification_happiness_pct: float
    top_trending_products: List[Dict[str, Any]]
    conversion_funnel_summary: Dict[str, Any]
    timestamp: datetime


class AIInsightSchema(BaseModel):
    id: int
    title: str
    category: str
    narrative_text: str
    confidence_score: float
    impact_level: str
    created_at: datetime


class AIOpsHealthSchema(BaseModel):
    product_knowledge_graph_status: str
    matching_engine_accuracy_pct: float
    recommendation_engine_latency_ms: float
    search_engine_latency_ms: float
    price_intelligence_accuracy_pct: float
    notification_platform_happiness_pct: float
    cache_hit_ratio_pct: float
    overall_health: str
