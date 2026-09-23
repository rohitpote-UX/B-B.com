"""
Brand Battle — Catalog Ingestion Admin Router
Provides administrative APIs for managing sources, running jobs,
monitoring metrics, and reviewing quarantined candidates.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
import os
import shutil
import tempfile
import logging

from database import get_db
import models
from catalog_engine.schemas import (
    CatalogSourceSchema,
    JobProgressResponse,
    CatalogMetricsResponse,
)
from catalog_engine.job_runner import CatalogJobRunner

logger = logging.getLogger("brandbattle.catalog.router")

router = APIRouter(prefix="/api/catalog", tags=["Catalog Ingestion (Admin)"])


@router.get("/sources", response_model=List[CatalogSourceSchema], summary="List all registered catalog sources")
async def list_sources(db: Session = Depends(get_db)):
    """Returns all registered catalog sources ordered by priority."""
    sources = db.query(models.CatalogSource).order_by(models.CatalogSource.priority.asc()).all()
    return [
        CatalogSourceSchema(
            id=s.id,
            name=s.name,
            source_type=s.source_type,
            base_url=s.base_url,
            adapter_key=s.adapter_key,
            license_type=s.license_type,
            commercial_use_allowed=s.commercial_use_allowed,
            automated_access_allowed=s.automated_access_allowed,
            requires_auth=s.requires_auth,
            active=s.active,
            priority=s.priority,
            terms_url=s.terms_url,
            data_scope=s.data_scope,
            last_sync_at=s.last_sync_at,
        )
        for s in sources
    ]


@router.post("/sources", summary="Register or update a catalog source")
async def register_source(
    name: str,
    source_type: str,
    adapter_key: str,
    base_url: Optional[str] = None,
    license_type: Optional[str] = None,
    priority: int = 10,
    terms_url: Optional[str] = None,
    data_scope: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Registers a new legally compliant source in the catalog registry."""
    existing = db.query(models.CatalogSource).filter(models.CatalogSource.name == name).first()
    if existing:
        existing.source_type = source_type
        existing.adapter_key = adapter_key
        existing.base_url = base_url
        existing.license_type = license_type
        existing.priority = priority
        existing.terms_url = terms_url
        existing.data_scope = data_scope
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "source_id": existing.id}

    source = models.CatalogSource(
        name=name,
        source_type=source_type,
        adapter_key=adapter_key,
        base_url=base_url,
        license_type=license_type,
        priority=priority,
        terms_url=terms_url,
        data_scope=data_scope,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return {"status": "created", "source_id": source.id}


@router.get("/jobs", summary="List recent catalog ingestion jobs")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Lists recent catalog ingestion jobs."""
    q = db.query(models.CatalogIngestionJob)
    if source_id:
        q = q.filter(models.CatalogIngestionJob.source_id == source_id)

    total = q.count()
    offset = (page - 1) * page_size
    jobs = q.order_by(desc(models.CatalogIngestionJob.id)).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "jobs": [
            {
                "id": j.id,
                "source_id": j.source_id,
                "source_name": j.source.name if j.source else "Unknown",
                "job_type": j.job_type,
                "status": j.status,
                "records_seen": j.records_seen,
                "records_created": j.records_created,
                "records_updated": j.records_updated,
                "records_merged": j.records_merged,
                "records_reviewed": j.records_reviewed,
                "records_rejected": j.records_rejected,
                "records_failed": j.records_failed,
                "started_at": str(j.started_at) if j.started_at else None,
                "completed_at": str(j.completed_at) if j.completed_at else None,
            }
            for j in jobs
        ],
    }


@router.post("/jobs", summary="Trigger a new catalog ingestion job")
async def trigger_job(
    source_id: int,
    job_type: str = "FULL_SYNC",
    max_records: Optional[int] = Query(None, description="Optional cap on records to process"),
    batch_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Triggers an ingestion job for a registered catalog source."""
    source = db.get(models.CatalogSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Catalog source not found")

    job = CatalogJobRunner.run_job(
        source_id=source_id,
        job_type=job_type,
        max_records=max_records,
        batch_size=batch_size,
        db=db,
    )

    return {
        "job_id": job.id,
        "source_name": source.name,
        "status": job.status,
        "records_seen": job.records_seen,
        "records_created": job.records_created,
        "records_merged": job.records_merged,
        "records_reviewed": job.records_reviewed,
        "records_rejected": job.records_rejected,
    }


@router.get("/jobs/{job_id}/status", response_model=JobProgressResponse, summary="Inspect specific job status")
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Retrieves real-time progress and statistics for an ingestion job."""
    job = db.get(models.CatalogIngestionJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobProgressResponse(
        job_id=job.id,
        source_id=job.source_id,
        source_name=job.source.name if job.source else "Unknown",
        job_type=job.job_type,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        cursor=job.cursor,
        records_seen=job.records_seen,
        records_created=job.records_created,
        records_updated=job.records_updated,
        records_merged=job.records_merged,
        records_reviewed=job.records_reviewed,
        records_rejected=job.records_rejected,
        records_failed=job.records_failed,
        error_summary=job.error_summary if isinstance(job.error_summary, list) else None,
    )


@router.get("/metrics", response_model=CatalogMetricsResponse, summary="Catalog health and ingestion dashboard metrics")
async def get_catalog_metrics(db: Session = Depends(get_db)):
    """Aggregates catalog size, quality scores, and daily ingestion performance."""
    total_masters = db.query(models.MasterProduct).filter(models.MasterProduct.is_active == True).count()
    total_brands = db.query(models.Brand).count()
    total_cats = db.query(models.Category).count()
    total_offers = db.query(models.MarketplaceOffer).filter(models.MarketplaceOffer.deleted_at.is_(None)).count()
    total_prices = db.query(models.Price).count()
    active_sources = db.query(models.CatalogSource).filter(models.CatalogSource.active == True).count()
    pending_reviews = db.query(models.ReviewQueueItem).filter(models.ReviewQueueItem.status == models.ReviewQueueStatus.PENDING.value).count()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    jobs_today = db.query(models.CatalogIngestionJob).filter(models.CatalogIngestionJob.created_at >= today_start).count()

    records_seen_today = db.query(func.coalesce(func.sum(models.CatalogIngestionJob.records_seen), 0)).filter(
        models.CatalogIngestionJob.created_at >= today_start
    ).scalar() or 0

    records_created_today = db.query(func.coalesce(func.sum(models.CatalogIngestionJob.records_created), 0)).filter(
        models.CatalogIngestionJob.created_at >= today_start
    ).scalar() or 0

    records_updated_today = db.query(func.coalesce(func.sum(models.CatalogIngestionJob.records_updated), 0)).filter(
        models.CatalogIngestionJob.created_at >= today_start
    ).scalar() or 0

    # Calculate GTIN & image coverage
    masters_with_gtin = db.query(models.MasterProduct).filter(
        models.MasterProduct.global_sku.isnot(None),
        models.MasterProduct.is_active == True
    ).count()
    masters_with_image = db.query(models.MasterProduct).filter(
        models.MasterProduct.primary_image_url.isnot(None),
        models.MasterProduct.is_active == True
    ).count()

    gtin_pct = round((masters_with_gtin / max(total_masters, 1)) * 100, 1)
    image_pct = round((masters_with_image / max(total_masters, 1)) * 100, 1)

    avg_qual = db.query(func.coalesce(func.avg(models.MasterProduct.completeness_score), 0.0)).filter(
        models.MasterProduct.is_active == True
    ).scalar() or 0.0

    return CatalogMetricsResponse(
        total_master_products=total_masters,
        total_variants=0,
        total_brands=total_brands,
        total_categories=total_cats,
        total_marketplace_offers=total_offers,
        total_prices=total_prices,
        active_sources=active_sources,
        pending_review_count=pending_reviews,
        jobs_today=jobs_today,
        records_processed_today=int(records_seen_today),
        records_created_today=int(records_created_today),
        records_updated_today=int(records_updated_today),
        average_quality_score=round(float(avg_qual), 1),
        gtin_coverage_pct=gtin_pct,
        image_coverage_pct=image_pct,
    )


@router.get("/review-queue", summary="List quarantined items requiring admin review")
async def list_quarantine_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query("pending"),
    db: Session = Depends(get_db),
):
    """Lists quarantined candidates flagged for human-in-the-loop review."""
    q = db.query(models.ReviewQueueItem).filter(models.ReviewQueueItem.status == status)
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(desc(models.ReviewQueueItem.id)).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": it.id,
                "master_product_id": it.master_product_id,
                "trigger_reason": it.trigger_reason,
                "priority": it.priority,
                "status": it.status,
                "confidence_score": it.confidence_score,
                "metadata": it.metadata_json,
                "created_at": str(it.created_at) if it.created_at else None,
            }
            for it in items
        ]
    }


@router.post("/review-queue/{item_id}/resolve", summary="Resolve a quarantined review item")
async def resolve_review_item(
    item_id: int,
    action: str = Query(..., pattern="^(approve|merge|reject)$"),
    target_master_id: Optional[int] = None,
    decision_notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Resolves a quarantined item:
    - 'approve': Approves creation of new canonical master.
    - 'merge': Merges candidate into target_master_id.
    - 'reject': Permanently rejects candidate.
    """
    item = db.get(models.ReviewQueueItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")

    item.status = models.ReviewQueueStatus.APPROVED.value if action in ("approve", "merge") else models.ReviewQueueStatus.REJECTED.value
    item.decision_notes = decision_notes or f"Manual action: {action}"
    item.reviewed_at = datetime.now(timezone.utc)
    db.commit()

    return {"status": "resolved", "action": action, "item_id": item.id}


@router.post("/upload-import", summary="Upload CSV/JSON for Admin Catalog Import")
async def upload_catalog_file(
    file: UploadFile = File(...),
    max_records: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Accepts CSV or JSON file, saves to temporary staging location,
    and runs AdminFileImportAdapter ingestion.
    """
    if not file.filename.endswith((".csv", ".json")):
        raise HTTPException(status_code=400, detail="Only .csv and .json files are supported")

    suffix = ".csv" if file.filename.endswith(".csv") else ".json"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()

        # Find or create Admin Catalog Import source
        admin_source = db.query(models.CatalogSource).filter(models.CatalogSource.adapter_key == "admin_import").first()
        if not admin_source:
            admin_source = models.CatalogSource(
                name="Admin Catalog Import",
                source_type="ADMIN_IMPORT",
                adapter_key="admin_import",
                license_type="BrandBattle Authorized Catalog",
                priority=2,
            )
            db.add(admin_source)
            db.commit()
            db.refresh(admin_source)

        job = CatalogJobRunner.run_job(
            source_id=admin_source.id,
            job_type="FILE_IMPORT",
            file_path=temp_file.name,
            max_records=max_records,
            db=db,
        )

        return {
            "status": "success",
            "job_id": job.id,
            "filename": file.filename,
            "records_seen": job.records_seen,
            "records_created": job.records_created,
            "records_merged": job.records_merged,
            "records_reviewed": job.records_reviewed,
            "records_rejected": job.records_rejected,
        }
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
