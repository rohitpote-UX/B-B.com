"""
Brand Battle — Comparison Workspace Pydantic Schemas
Request and response schemas for AI decision workspace evaluation, questions, and saved states.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ComparisonRequestSchema(BaseModel):
    product1_id: int
    product2_id: int
    persona: Optional[str] = "general"
    scenario: Optional[str] = "default"  # price, performance, durability, long_term


class DecisionSummarySchema(BaseModel):
    recommended_product_id: int
    recommended_product_name: str
    confidence_score: float
    top_reasons: List[str]
    best_use_case: str
    estimated_savings_inr: float
    best_value_badge: str
    trade_off_summary: str


class SystemAgreementSchema(BaseModel):
    ai_recommendation: bool = True
    price_intelligence: bool = True
    product_knowledge_graph: bool = True
    marketplace_trust: bool = True
    value_engine: bool = True
    agreed_systems_count: int = 5
    total_systems_count: int = 5
    agreement_narrative: str


class HiddenCostSchema(BaseModel):
    product_id: int
    sticker_price_inr: float
    estimated_shipping_inr: float
    essential_accessories_inr: float
    annual_maintenance_inr: float
    total_5year_ownership_inr: float


class WorkspaceDecisionPayloadSchema(BaseModel):
    product1_id: int
    product2_id: int
    persona: str
    scenario: str
    decision_summary: DecisionSummarySchema
    system_agreement: SystemAgreementSchema
    hidden_costs: Dict[int, HiddenCostSchema]
    key_differences: List[Dict[str, Any]]
    confidence_meter: Dict[str, Any]
    social_proof: Dict[str, Any]
    decision_checklist: List[Dict[str, Any]]
    audit_timeline: List[str]
