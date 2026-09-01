"""
Brand Battle — Price Intelligence Pydantic Schemas
Request and response schemas for all 20 price intelligence sub-engines.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PriceAlertCreateSchema(BaseModel):
    product_id: int
    target_price: float
    drop_percentage: Optional[float] = None
    marketplace_filter: Optional[str] = None
    notify_email: str
    notify_sms: Optional[str] = None


class PriceAlertResponseSchema(BaseModel):
    id: int
    user_id: int
    product_id: int
    target_price: float
    drop_percentage: Optional[float] = None
    marketplace_filter: Optional[str] = None
    notify_email: str
    is_active: bool
    created_at: datetime


class PriceTimelineSummarySchema(BaseModel):
    h24_lowest: float
    d7_lowest: float
    d30_lowest: float
    d90_lowest: float
    m6_lowest: float
    y1_lowest: float
    lifetime_lowest: float
    lifetime_highest: float
    average_price: float


class BuyRecommendationSchema(BaseModel):
    decision: str                      # BUY NOW, WAIT, EXCELLENT DEAL, GOOD DEAL, OVERPRICED, NOT RECOMMENDED
    confidence_score: float             # 0.0 - 1.0
    reasoning: str
    predicted_savings: float
    expected_waiting_period_days: int
    probability_of_future_drop: float  # 0.0 - 1.0


class FairMarketValueSchema(BaseModel):
    current_price: float
    fair_price: float
    price_difference: float
    overpriced_percentage: float
    underpriced_percentage: float
    status: str                         # Fairly Priced, Underpriced, Overpriced


class FakeDiscountSchema(BaseModel):
    claimed_mrp: float
    historical_avg_mrp: float
    current_price: float
    claimed_discount_pct: float
    real_discount_pct: float
    fake_discount_pct: float
    is_manipulated: bool
    trust_score: float


class MarketplaceTrustSchema(BaseModel):
    marketplace: str
    trust_score: float
    delivery_speed_score: float
    refund_success_score: float
    seller_reliability_score: float
    inventory_accuracy_score: float
    price_stability_score: float
    warranty_quality_score: float
    customer_satisfaction_score: float


class PriceForecastSchema(BaseModel):
    d7_predicted_price: float
    d30_predicted_price: float
    d90_predicted_price: float
    next_festival_predicted_price: float
    confidence_interval_low: float
    confidence_interval_high: float
    forecast_trend: str               # Falling, Stable, Rising
    explanation: str


class VolatilitySchema(BaseModel):
    variance: float
    standard_deviation: float
    volatility_score: float
    classification: str               # Stable, Moderately Volatile, Highly Volatile
    change_frequency: str


class TotalCostOfOwnershipSchema(BaseModel):
    purchase_price: float
    shipping_cost: float
    tax_cost: float
    accessories_cost: float
    annual_maintenance: float
    estimated_repairs_3yr: float
    total_3yr_tco: float
    effective_monthly_cost: float


class HiddenCostSchema(BaseModel):
    shipping: float
    taxes: float
    installation: float
    mandatory_accessories: float
    emi_interest: float
    platform_fee: float
    final_payable_cost: float


class SmartBundleSchema(BaseModel):
    bundle_name: str
    item_ids: List[int]
    item_names: List[str]
    individual_total: float
    bundle_price: float
    savings_amount: float
    savings_percentage: float


class NegotiationAssistantSchema(BaseModel):
    current_price: float
    recommended_counter_offer: float
    fair_value: float
    acceptance_probability_pct: float
    talking_points: List[str]


class PriceIntelligenceReportSchema(BaseModel):
    product_id: int
    product_name: str
    brand: Optional[str]
    category: Optional[str]
    current_best_price: float
    original_price: float
    opportunity_score: float
    buy_confidence_score: float
    market_heat_status: str
    buy_recommendation: BuyRecommendationSchema
    fair_market_value: FairMarketValueSchema
    fake_discount_audit: FakeDiscountSchema
    marketplace_trust: MarketplaceTrustSchema
    forecast: PriceForecastSchema
    volatility: VolatilitySchema
    hidden_costs: HiddenCostSchema
    tco: TotalCostOfOwnershipSchema
    negotiation: NegotiationAssistantSchema
    bundles: List[SmartBundleSchema]
    explanation: str
    timestamp: str
