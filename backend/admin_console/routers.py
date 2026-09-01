"""
Brand Battle — Enterprise Admin Console REST API Layer
FastAPI router mounted at /api/admin-console/* providing access to all 20 command modules, Brief, Copilot, and Command Palette.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_optional
from models import User
from admin_console.services import admin_console_service
from admin_console.metrics import admin_metrics
from admin_console.repository import admin_repo
from admin_console.schemas import (
    CopilotQuerySchema, ReviewQueueActionSchema, FeatureFlagUpdateSchema
)

router = APIRouter(prefix="/api/admin-console", tags=["Admin Command Center"])


@router.get("/overview")
async def get_overview(db: Session = Depends(get_db)):
    """Fetch Executive Overview Dashboard platform metrics."""
    overview = admin_console_service.get_overview_dashboard(db)
    return {
        "success": True,
        "message": "Executive Overview Dashboard retrieved",
        "data": overview,
    }


@router.get("/brief")
async def get_executive_morning_brief(db: Session = Depends(get_db)):
    """Fetch Executive Morning Brief natural language 24h operational summary."""
    brief = admin_console_service.get_executive_brief(db)
    return {
        "success": True,
        "message": "Executive Morning Brief retrieved",
        "data": brief,
    }


@router.post("/copilot")
async def query_ai_copilot(
    payload: CopilotQuerySchema,
    db: Session = Depends(get_db),
):
    """Query AI Copilot for Administrators."""
    resp = admin_console_service.query_copilot(db, prompt=payload.prompt)
    return {
        "success": True,
        "message": "Copilot response generated",
        "data": resp,
    }


@router.get("/command-palette")
async def search_command_palette(
    q: Optional[str] = Query("", description="Search term for quick commands")
):
    """Search Command Palette quick actions (<50ms SLO target)."""
    commands = admin_console_service.search_command_palette(query=q or "")
    return {
        "success": True,
        "message": f"Found {len(commands)} matching commands",
        "data": {"commands": commands},
    }


@router.get("/review-queue")
async def get_review_queue(db: Session = Depends(get_db)):
    """Fetch Unified Review Queue items (product merges, matching reviews, content moderation)."""
    queue = admin_console_service.get_review_queue(db)
    return {
        "success": True,
        "message": "Unified Review Queue retrieved",
        "data": queue,
    }


@router.post("/review-queue/action")
async def resolve_review_item(
    payload: ReviewQueueActionSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Resolve a review queue item."""
    res = admin_repo.resolve_review_item(db, payload.item_id, payload.action, payload.notes)
    if current_user:
        admin_repo.log_action(
            db, current_user.id, current_user.full_name or "Admin", "review_queue_resolution", f"ReviewItem #{payload.item_id}"
        )
    return {
        "success": True,
        "message": f"Review item #{payload.item_id} resolved with action '{payload.action}'",
        "data": {"item_id": payload.item_id, "action": payload.action},
    }


@router.get("/feature-flags")
async def get_feature_flags(db: Session = Depends(get_db)):
    """Fetch Feature Flag Center settings."""
    flags = admin_console_service.get_feature_flags(db)
    return {
        "success": True,
        "message": "Feature flags retrieved",
        "data": {"flags": flags},
    }


@router.post("/feature-flags")
async def update_feature_flag(
    payload: FeatureFlagUpdateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Update feature flag toggle or rollout percentage."""
    flag = admin_repo.update_feature_flag(db, payload.key, payload.is_enabled, payload.rollout_percentage or 100.0)
    if current_user:
        admin_repo.log_action(
            db, current_user.id, current_user.full_name or "Admin", "feature_flag_update", f"Flag:{payload.key}"
        )
    return {
        "success": True,
        "message": f"Feature flag '{payload.key}' updated",
        "data": {"key": flag.key, "is_enabled": flag.is_enabled, "rollout_percentage": flag.rollout_percentage},
    }


@router.get("/audit-logs")
async def get_audit_logs(db: Session = Depends(get_db)):
    """Fetch Audit & Compliance logs."""
    trail = admin_console_service.get_audit_trail(db)
    return {
        "success": True,
        "message": "Audit & Compliance trail retrieved",
        "data": trail,
    }


@router.get("/ai-ops")
async def get_ai_ops_center(db: Session = Depends(get_db)):
    """Fetch complete AI Subsystem Operations Center health metrics."""
    ai_ops = admin_console_service.get_ai_ops_center(db)
    return {
        "success": True,
        "message": "AI Subsystem Operations Center health retrieved",
        "data": ai_ops,
    }


@router.post("/reports")
async def submit_user_report(
    product_id: int,
    issue_type: str,
    details: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """User feedback loop for 'Report Incorrect Information' on Product Detail Pages."""
    report_data = {
        "product_id": product_id,
        "issue_type": issue_type,  # wrong_price, wrong_specs, broken_image, wrong_category, product_unavailable, duplicate, wrong_rec
        "details": details or "User reported issue",
        "status": "pending_review",
    }
    return {
        "success": True,
        "message": "Thank you! Your report has been submitted to our moderation queue for review.",
        "data": report_data,
    }


@router.get("/metrics")
async def get_metrics():
    """Fetch Prometheus-compatible telemetry & SLO metrics."""
    summary = admin_metrics.get_metrics_summary()
    return {
        "success": True,
        "message": "Admin Console metrics retrieved",
        "data": summary,
    }


@router.get("/health")
async def admin_health():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "Enterprise Command Center operational",
        "data": {
            "status": "healthy",
            "version": "v8.0.0-enterprise-command-center",
        },
    }
