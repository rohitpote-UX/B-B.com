"""
Brand Battle — Enterprise Analytics Platform REST API Layer
FastAPI router mounted at /api/analytics/* exposing event ingestion, dashboards, AI insights, funnels, and ops health.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_optional
from models import User
from analytics_platform.services import analytics_platform_service
from analytics_platform.metrics import analytics_metrics
from analytics_platform.realtime_stream import realtime_stream_analytics
from analytics_platform.funnel_engine import funnel_analytics_engine
from analytics_platform.segmentation import user_segmentation_engine
from analytics_platform.schemas import EventIngestSchema, BatchEventIngestSchema

router = APIRouter(prefix="/api/analytics", tags=["Analytics Platform"])


@router.post("/events")
async def ingest_event(
    payload: EventIngestSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Ingest a single structured analytics event (<20ms latency target)."""
    user_id = current_user.id if current_user else payload.user_id
    res = analytics_platform_service.ingest_event(
        db=db,
        event_category=payload.event_category,
        event_type=payload.event_type,
        user_id=user_id,
        session_id=payload.session_id or "guest_session",
        device_type=payload.device_type or "desktop",
        payload=payload.payload,
    )
    return {
        "success": True,
        "message": f"Event '{payload.event_type}' ingested successfully",
        "data": res,
    }


@router.post("/events/batch")
async def ingest_events_batch(
    payload: BatchEventIngestSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Ingest a batch of analytics events."""
    user_id = current_user.id if current_user else None
    results = []
    for evt in payload.events:
        uid = user_id or evt.user_id
        res = analytics_platform_service.ingest_event(
            db=db,
            event_category=evt.event_category,
            event_type=evt.event_type,
            user_id=uid,
            session_id=evt.session_id or "guest_session",
            device_type=evt.device_type or "desktop",
            payload=evt.payload,
        )
        results.append(res)

    return {
        "success": True,
        "message": f"Ingested batch of {len(results)} events",
        "data": {"count": len(results)},
    }


@router.get("/dashboard")
async def get_executive_dashboard(db: Session = Depends(get_db)):
    """Fetch decision-ready Executive Dashboard summary (DAU, MAU, Retention, Conversions)."""
    dashboard = analytics_platform_service.get_executive_dashboard(db)
    return {
        "success": True,
        "message": "Executive Decision Dashboard retrieved",
        "data": dashboard,
    }


@router.get("/ai-insights")
async def get_ai_insights(db: Session = Depends(get_db)):
    """Fetch plain-language AI insights and active anomaly alerts."""
    data = analytics_platform_service.get_ai_insights_and_anomalies(db)
    return {
        "success": True,
        "message": "AI Decision Insights retrieved",
        "data": data,
    }


@router.get("/funnels")
async def get_funnels(
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Fetch conversion funnel analytics and drop-off bottleneck isolation."""
    funnel = funnel_analytics_engine.compute_funnel(db, funnel_name=name or "Search to Purchase Intent")
    return {
        "success": True,
        "message": "Funnel conversion analytics retrieved",
        "data": funnel,
    }


@router.get("/realtime")
async def get_realtime_stream():
    """Fetch live streaming analytics metrics (active users, searches/min, comparisons/min)."""
    metrics = realtime_stream_analytics.get_realtime_metrics()
    return {
        "success": True,
        "message": "Real-time streaming analytics retrieved",
        "data": metrics,
    }


@router.get("/segments")
async def get_user_segments(db: Session = Depends(get_db)):
    """Fetch dynamic user cohort segmentation summary."""
    summary = user_segmentation_engine.get_user_segment_summary(db)
    return {
        "success": True,
        "message": "User segmentation cohorts retrieved",
        "data": summary,
    }


@router.get("/ai-ops")
async def get_ai_ops_health(db: Session = Depends(get_db)):
    """Fetch AI Subsystem Operations Center health metrics."""
    health = analytics_platform_service.get_ai_ops_health(db)
    return {
        "success": True,
        "message": "AI Subsystem Operations Center health retrieved",
        "data": health,
    }


@router.get("/metrics")
async def get_metrics():
    """Fetch Prometheus-compatible telemetry & P95 query latency metrics."""
    summary = analytics_metrics.get_metrics_summary()
    return {
        "success": True,
        "message": "Analytics Platform metrics retrieved",
        "data": summary,
    }


@router.get("/health")
async def analytics_health():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "Decision Intelligence & Analytics Platform operational",
        "data": {
            "status": "healthy",
            "version": "v7.0.0-enterprise-analytics-platform",
        },
    }
