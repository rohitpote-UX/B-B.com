"""
Brand Battle - Pipeline & Observability Router
Exposes API endpoints for pipeline execution, ingestion triggering, real-time throughput stats, and DLQ audits.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from database import get_db
from pipeline.orchestrator import pipeline_orchestrator
from pipeline.scrapers.marketplace_scrapers import get_all_scrapers
from pipeline.queue import queue_manager
from pipeline.monitoring import pipeline_monitor

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline & Data Ingestion"])


@router.post("/ingest", summary="Trigger real-time data ingestion pipeline")
async def trigger_ingestion(
    category_or_keyword: Optional[str] = "Smartphones",
    payloads: Optional[List[Dict[str, Any]]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Ingests custom product payloads or triggers active marketplace scrapers asynchronously.
    """
    if payloads:
        # Run custom payloads through pipeline batch
        result = pipeline_orchestrator.run_pipeline_batch(payloads, db)
        return {
            "status": "success",
            "message": "Processed custom payload batch through pipeline",
            "metrics": result
        }

    # Trigger distributed scrapers
    scrapers = get_all_scrapers()
    all_raw_items = []
    
    for s in scrapers:
        items = s.run_safe(category_or_keyword)
        for it in items:
            all_raw_items.append(it.dict())
            queue_manager.publish_raw(it.dict())

    # Process extracted items through orchestrator
    result = pipeline_orchestrator.run_pipeline_batch(all_raw_items, db)

    return {
        "status": "success",
        "scrapers_executed": len(scrapers),
        "total_extracted": len(all_raw_items),
        "processing_result": result
    }


@router.get("/stats", summary="Get real-time pipeline performance metrics")
async def get_pipeline_stats():
    """Returns throughput, validation pass/fail, AI matching metrics, and queue depth."""
    stats = pipeline_monitor.get_summary()
    queue_metrics = queue_manager.get_queue_depth()
    stats["queue"] = queue_metrics
    return stats


@router.get("/scrapers", summary="Get marketplace scraper health metrics")
async def get_scrapers_health():
    """Returns operational health status for Amazon, Flipkart, Croma, Reliance, Myntra, and Ajio scrapers."""
    scrapers = get_all_scrapers()
    return [s.get_health_status() for s in scrapers]


@router.get("/dlq", summary="View Dead-Letter Queue records")
async def get_dlq_records(limit: int = 20):
    """Fetches records failing validation or quality threshold checks for pipeline audit."""
    return queue_manager.get_dlq_records(count=limit)
