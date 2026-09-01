"""
Brand Battle — Admin Console Pydantic Schemas
Request and response schemas for briefs, copilot, command palette, review queue, feature flags, and audit logs.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ExecutiveBriefSchema(BaseModel):
    date_str: str
    narrative_summary: str
    metrics_summary: Dict[str, Any]
    created_at: datetime


class CopilotQuerySchema(BaseModel):
    prompt: str


class CopilotResponseSchema(BaseModel):
    prompt: str
    answer: str
    source_data: Dict[str, Any]
    confidence: float = 0.95


class CommandPaletteResultSchema(BaseModel):
    id: str
    title: str
    category: str
    action_type: str  # navigate, execute, search
    target_url: Optional[str] = None


class ReviewQueueActionSchema(BaseModel):
    item_id: int
    action: str  # approve, reject, resolve
    notes: Optional[str] = None


class FeatureFlagUpdateSchema(BaseModel):
    key: str
    is_enabled: bool
    rollout_percentage: Optional[float] = 100.0


class AuditLogSchema(BaseModel):
    id: int
    admin_name: str
    action_type: str
    target_resource: str
    created_at: datetime
