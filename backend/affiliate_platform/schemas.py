"""
Brand Battle — Affiliate Platform Pydantic Schemas
Request and response schemas for deep link generation, click logging, conversions, and commission dashboards.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DeepLinkRequestSchema(BaseModel):
    product_id: int
    destination_url: str
    marketplace_name: Optional[str] = "Amazon"
    touchpoint: Optional[str] = "search"
    session_id: Optional[str] = "guest_session"


class DeepLinkResponseSchema(BaseModel):
    link_token: str
    product_id: int
    provider_key: str
    destination_url: str
    affiliate_url: str
    redirect_url: str
    is_fallback: bool = False


class ClickLogRequestSchema(BaseModel):
    link_token: str
    touchpoint: Optional[str] = "search"
    session_id: Optional[str] = "guest_session"


class ConversionLogRequestSchema(BaseModel):
    provider_key: str
    order_id: Optional[str] = None
    click_id: Optional[str] = None
    sale_amount_inr: float
    commission_amount_inr: float


class CommissionDashboardSchema(BaseModel):
    total_clicks: int
    total_conversions: int
    total_revenue_inr: float
    total_commission_inr: float
    conversion_rate_pct: float
    epc_inr: float
    top_provider: str
    timestamp: datetime
