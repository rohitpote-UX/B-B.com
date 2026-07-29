"""
Brand Battle - Knowledge Graph Admin Router
Internal admin-only endpoints for inspecting, managing, and monitoring the Product Knowledge Graph.
No frontend consumption — these are backend management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional, List

from database import get_db
from knowledge_graph.kg_service import kg_service
from knowledge_graph.relationship_engine import RelationshipEngine
import models
import logging

logger = logging.getLogger("brandbattle.kg.router")

router = APIRouter(prefix="/api/kg", tags=["Knowledge Graph (Admin)"])

relationship_engine = RelationshipEngine()


@router.get("/stats", summary="Get Knowledge Graph health metrics")
async def get_kg_stats(db: Session = Depends(get_db)):
    """Returns overall Knowledge Graph health statistics."""
    # Check cache first
    cached = kg_service.cache.get_stats()
    if cached:
        return cached

    metrics = kg_service.compute_graph_metrics(db)
    return metrics


@router.get("/masters", summary="List master products")
async def list_masters(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    brand: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all MasterProducts with offer counts and filtering."""
    q = db.query(models.MasterProduct).filter(models.MasterProduct.is_active == True)

    if brand:
        q = q.join(models.Brand, models.MasterProduct.brand_id == models.Brand.id).filter(
            models.Brand.slug == brand
        )
    if category:
        q = q.join(models.Category, models.MasterProduct.category_id == models.Category.id).filter(
            models.Category.slug == category
        )
    if search:
        q = q.filter(models.MasterProduct.canonical_name.ilike(f"%{search}%"))

    total = q.count()
    offset = (page - 1) * page_size

    masters = (
        q.options(
            joinedload(models.MasterProduct.brand),
            joinedload(models.MasterProduct.category),
        )
        .order_by(desc(models.MasterProduct.offer_count))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "masters": [
            {
                "id": m.id,
                "uuid": m.uuid,
                "canonical_name": m.canonical_name,
                "slug": m.slug,
                "brand": m.brand.name if m.brand else None,
                "category": m.category.name if m.category else None,
                "product_type": m.product_type,
                "model_series": m.model_series,
                "model_name": m.model_name,
                "color_family": m.color_family,
                "material": m.material,
                "gender": m.gender,
                "offer_count": m.offer_count,
                "lowest_price": m.lowest_price,
                "highest_price": m.highest_price,
                "average_rating": m.average_rating,
                "confidence_score": m.confidence_score,
                "is_verified": m.is_verified,
                "created_at": str(m.created_at) if m.created_at else None,
            }
            for m in masters
        ],
    }


@router.get("/masters/{master_id}", summary="Get master product detail")
async def get_master_detail(master_id: int, db: Session = Depends(get_db)):
    """Get full MasterProduct detail with all offers, attributes, and relationships."""
    master = (
        db.query(models.MasterProduct)
        .filter(models.MasterProduct.id == master_id)
        .options(
            joinedload(models.MasterProduct.brand),
            joinedload(models.MasterProduct.category),
            joinedload(models.MasterProduct.offers),
            joinedload(models.MasterProduct.attributes),
            joinedload(models.MasterProduct.tags),
            joinedload(models.MasterProduct.kg_images),
        )
        .first()
    )

    if not master:
        raise HTTPException(status_code=404, detail="Master product not found")

    return {
        "id": master.id,
        "uuid": master.uuid,
        "canonical_name": master.canonical_name,
        "slug": master.slug,
        "brand": master.brand.name if master.brand else None,
        "category": master.category.name if master.category else None,
        "description": master.description,
        "ai_summary": master.ai_summary,
        "gender": master.gender,
        "color_family": master.color_family,
        "material": master.material,
        "product_type": master.product_type,
        "model_series": master.model_series,
        "model_name": master.model_name,
        "variant": master.variant,
        "release_year": master.release_year,
        "global_sku": master.global_sku,
        "specifications": master.specifications,
        "features": master.features,
        "images": master.images,
        "primary_image_url": master.primary_image_url,
        "offer_count": master.offer_count,
        "lowest_price": master.lowest_price,
        "highest_price": master.highest_price,
        "average_rating": master.average_rating,
        "total_reviews": master.total_reviews,
        "confidence_score": master.confidence_score,
        "is_verified": master.is_verified,
        "offers": [
            {
                "id": o.id,
                "marketplace": o.marketplace,
                "title": o.title,
                "price": o.price,
                "original_price": o.original_price,
                "discount_percentage": o.discount_percentage,
                "seller_name": o.seller_name,
                "rating": o.rating,
                "review_count": o.review_count,
                "is_available": o.is_available,
                "url": o.url,
                "match_confidence": o.match_confidence,
                "last_scraped": str(o.last_scraped) if o.last_scraped else None,
            }
            for o in master.offers
        ],
        "attributes": [
            {
                "name": a.attribute_name,
                "value": a.attribute_value,
                "type": a.attribute_type,
                "unit": a.unit,
            }
            for a in master.attributes
        ],
        "tags": [
            {"tag": t.tag, "type": t.tag_type}
            for t in master.tags
        ],
        "images_detail": [
            {
                "url": i.url,
                "source": i.source_marketplace,
                "is_primary": i.is_primary,
            }
            for i in master.kg_images
        ],
        "linked_product_ids": [p.id for p in master.products],
    }


@router.get("/masters/{master_id}/relationships", summary="Get relationships for a master")
async def get_master_relationships(
    master_id: int,
    relationship_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all relationships for a MasterProduct."""
    master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master product not found")

    relationships = relationship_engine.get_related_masters(master_id, db, relationship_type)
    return {
        "master_id": master_id,
        "canonical_name": master.canonical_name,
        "relationship_count": len(relationships),
        "relationships": relationships,
    }


@router.get("/masters/{master_id}/offers", summary="Get marketplace offers for a master")
async def get_master_offers(master_id: int, db: Session = Depends(get_db)):
    """Get all marketplace offers linked to a MasterProduct."""
    master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master product not found")

    offers = (
        db.query(models.MarketplaceOffer)
        .filter(models.MarketplaceOffer.master_product_id == master_id)
        .order_by(models.MarketplaceOffer.price.asc())
        .all()
    )

    return {
        "master_id": master_id,
        "canonical_name": master.canonical_name,
        "offer_count": len(offers),
        "offers": [
            {
                "id": o.id,
                "marketplace": o.marketplace,
                "title": o.title,
                "price": o.price,
                "original_price": o.original_price,
                "discount_percentage": o.discount_percentage,
                "currency": o.currency,
                "seller_name": o.seller_name,
                "seller_rating": o.seller_rating,
                "rating": o.rating,
                "review_count": o.review_count,
                "is_available": o.is_available,
                "stock_status": o.stock_status,
                "url": o.url,
                "match_confidence": o.match_confidence,
                "status": o.status,
                "last_scraped": str(o.last_scraped) if o.last_scraped else None,
            }
            for o in offers
        ],
    }


@router.get("/orphans", summary="Get products without a master")
async def get_orphan_products(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get products that are not linked to any MasterProduct."""
    orphans = (
        db.query(models.Product)
        .filter(
            models.Product.master_product_id == None,
            models.Product.is_active == True,
        )
        .limit(limit)
        .all()
    )

    return {
        "orphan_count": len(orphans),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "brand_id": p.brand_id,
                "category_id": p.category_id,
                "current_best_price": p.current_best_price,
            }
            for p in orphans
        ],
    }


@router.post("/merge", summary="Merge two master products")
async def merge_masters(
    source_id: int,
    target_id: int,
    db: Session = Depends(get_db),
):
    """Merge source MasterProduct into target. Moves all offers and relationships."""
    if source_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot merge a master into itself")

    success = kg_service.merge_masters(source_id, target_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="One or both master products not found")

    db.commit()
    return {"status": "success", "message": f"Master {source_id} merged into {target_id}"}


@router.post("/relationships", summary="Add a product relationship")
async def add_relationship(
    source_id: int,
    target_id: int,
    relationship_type: str,
    confidence: float = 1.0,
    bidirectional: bool = False,
    db: Session = Depends(get_db),
):
    """Manually add a relationship between two MasterProducts."""
    source = db.query(models.MasterProduct).filter(models.MasterProduct.id == source_id).first()
    target = db.query(models.MasterProduct).filter(models.MasterProduct.id == target_id).first()
    if not source or not target:
        raise HTTPException(status_code=404, detail="One or both masters not found")

    # Validate relationship type
    valid_types = [rt.value for rt in models.RelationshipType]
    if relationship_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid relationship type. Valid: {valid_types}"
        )

    rel = models.ProductRelationship(
        source_master_id=source_id,
        target_master_id=target_id,
        relationship_type=relationship_type,
        confidence=confidence,
        is_bidirectional=bidirectional,
    )
    db.add(rel)
    db.commit()

    return {"status": "success", "relationship_id": rel.id}


@router.post("/detect-relationships/{master_id}", summary="Auto-detect relationships")
async def detect_relationships(master_id: int, db: Session = Depends(get_db)):
    """Run auto-relationship detection for a MasterProduct."""
    master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master product not found")

    created = relationship_engine.detect_relationships(master_id, db)
    db.commit()

    return {
        "master_id": master_id,
        "relationships_detected": len(created),
        "relationships": created,
    }


@router.post("/sync", summary="Re-sync all masters to product table")
async def sync_all_masters(db: Session = Depends(get_db)):
    """Re-sync all MasterProducts to their corresponding Product table records."""
    masters = db.query(models.MasterProduct).filter(models.MasterProduct.is_active == True).all()
    synced = 0
    for master in masters:
        try:
            kg_service.sync_product_from_master(master, db)
            synced += 1
        except Exception as e:
            logger.error(f"Failed to sync master {master.id}: {e}")

    db.commit()
    return {"status": "success", "synced": synced, "total_masters": len(masters)}


@router.post("/detect-all-relationships", summary="Auto-detect relationships for all masters")
async def detect_all_relationships(db: Session = Depends(get_db)):
    """Run auto-relationship detection for all active MasterProducts."""
    masters = db.query(models.MasterProduct).filter(models.MasterProduct.is_active == True).all()
    total_created = 0
    for master in masters:
        created = relationship_engine.detect_relationships(master.id, db)
        total_created += len(created)

    db.commit()
    return {
        "status": "success",
        "masters_processed": len(masters),
        "relationships_created": total_created,
    }


# ─── Enterprise Hardening Endpoints ─────────────────────────────────

@router.get("/health-dashboard", summary="Enterprise Knowledge Graph Health Dashboard")
async def get_kg_health_dashboard(db: Session = Depends(get_db)):
    """Returns comprehensive health, quality, completeness, and freshness metrics."""
    metrics = kg_service.compute_graph_metrics(db)

    # Calculate additional metrics
    low_confidence_count = db.query(func.count(models.MasterProduct.id)).filter(
        models.MasterProduct.confidence_score < 0.70,
        models.MasterProduct.is_active == True,
    ).scalar() or 0

    pending_reviews_count = db.query(func.count(models.ReviewQueueItem.id)).filter(
        models.ReviewQueueItem.status == models.ReviewQueueStatus.PENDING.value
    ).scalar() or 0

    avg_completeness = db.query(func.avg(models.MasterProduct.completeness_score)).filter(
        models.MasterProduct.is_active == True
    ).scalar() or 0.0

    products_without_images = db.query(func.count(models.MasterProduct.id)).filter(
        models.MasterProduct.primary_image_url == None,
        models.MasterProduct.is_active == True
    ).scalar() or 0

    audit_events_count = db.query(func.count(models.GraphAuditEvent.id)).scalar() or 0
    versions_count = db.query(func.count(models.MasterProductVersion.id)).scalar() or 0

    metrics.update({
        "low_confidence_masters": low_confidence_count,
        "pending_review_queue": pending_reviews_count,
        "avg_completeness_score": round(avg_completeness, 1),
        "products_without_images": products_without_images,
        "total_audit_events": audit_events_count,
        "total_version_snapshots": versions_count,
    })

    return metrics


@router.get("/audit-log", summary="Queryable Graph Audit Log")
async def get_audit_log(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Query immutable graph audit trail."""
    q = db.query(models.GraphAuditEvent)
    if entity_type:
        q = q.filter(models.GraphAuditEvent.entity_type == entity_type)
    if action:
        q = q.filter(models.GraphAuditEvent.action == action)

    total = q.count()
    offset = (page - 1) * page_size
    events = q.order_by(desc(models.GraphAuditEvent.created_at)).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "events": [
            {
                "event_id": e.event_id,
                "correlation_id": e.correlation_id,
                "actor": e.actor,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "action": e.action,
                "previous_value": e.previous_value,
                "new_value": e.new_value,
                "reason": e.reason,
                "created_at": str(e.created_at),
            }
            for e in events
        ],
    }


@router.get("/masters/{master_id}/versions", summary="Get version history for a master product")
async def get_master_versions(master_id: int, db: Session = Depends(get_db)):
    """Returns immutable version history for a MasterProduct."""
    from knowledge_graph.versioning import version_manager
    history = version_manager.get_version_history(master_id, db)
    return {"master_id": master_id, "version_count": len(history), "versions": history}


@router.get("/masters/{master_id}/versions/compare", summary="Compare two product versions")
async def compare_master_versions(
    master_id: int,
    v1_id: int,
    v2_id: int,
    db: Session = Depends(get_db),
):
    """Compares two historical MasterProductVersion records side-by-side."""
    from knowledge_graph.versioning import version_manager
    return version_manager.compare_versions(v1_id, v2_id, db)


@router.post("/masters/{master_id}/rollback", summary="Rollback master product to a version")
async def rollback_master_version(
    master_id: int,
    version_number: int,
    actor: str = "admin",
    db: Session = Depends(get_db),
):
    """Rolls back a MasterProduct to a specified historical version number."""
    from knowledge_graph.versioning import version_manager
    success, message = version_manager.rollback_to_version(master_id, version_number, actor=actor, db=db)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    db.commit()
    return {"status": "success", "message": message}


@router.get("/review-queue", summary="List pending manual review queue items")
async def get_review_queue(
    status: str = "pending",
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List pending review items for low-confidence or uncertain matches."""
    q = db.query(models.ReviewQueueItem)
    if status:
        q = q.filter(models.ReviewQueueItem.status == status)
    if priority:
        q = q.filter(models.ReviewQueueItem.priority == priority)

    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(desc(models.ReviewQueueItem.created_at)).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": i.id,
                "master_product_id": i.master_product_id,
                "offer_id": i.offer_id,
                "trigger_reason": i.trigger_reason,
                "priority": i.priority,
                "status": i.status,
                "confidence_score": i.confidence_score,
                "metadata": i.metadata_json,
                "created_at": str(i.created_at),
            }
            for i in items
        ],
    }


@router.post("/review-queue/{item_id}/action", summary="Process manual review queue decision")
async def process_review_action(
    item_id: int,
    action: str,  # approve, reject, merge, split, reprocess
    reviewer_id: int = 1,
    notes: Optional[str] = None,
    target_master_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Approve, reject, merge, split, or reprocess a pending review item."""
    from knowledge_graph.review_queue import review_queue_engine
    success, message = review_queue_engine.process_decision(
        queue_item_id=item_id,
        action=action,
        reviewer_id=reviewer_id,
        notes=notes,
        target_master_id=target_master_id,
        db=db,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    db.commit()
    return {"status": "success", "message": message}


@router.get("/graph-traversal/{master_id}", summary="Multi-hop weighted graph traversal")
async def get_graph_traversal(
    master_id: int,
    depth: int = Query(2, ge=1, le=4),
    max_nodes: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Traverse product relationship graph network starting from root master product."""
    return relationship_engine.get_weighted_graph_traversal(master_id, db, depth=depth, max_nodes=max_nodes)


@router.post("/masters/{master_id}/soft-delete", summary="Soft delete a master product")
async def soft_delete_master(
    master_id: int,
    reason: str = "Admin soft deletion",
    actor: str = "admin",
    db: Session = Depends(get_db),
):
    """Soft delete a MasterProduct without permanently deleting data."""
    success = kg_service.soft_delete_master(master_id, reason=reason, actor=actor, db=db)
    if not success:
        raise HTTPException(status_code=404, detail="Master product not found")
    db.commit()
    return {"status": "success", "message": f"Master product {master_id} soft deleted"}


@router.post("/masters/{master_id}/restore", summary="Restore a soft-deleted master product")
async def restore_master(
    master_id: int,
    actor: str = "admin",
    db: Session = Depends(get_db),
):
    """Restore a soft-deleted MasterProduct to active state."""
    success = kg_service.restore_master(master_id, actor=actor, db=db)
    if not success:
        raise HTTPException(status_code=404, detail="Master product not found")
    db.commit()
    return {"status": "success", "message": f"Master product {master_id} restored to active state"}


@router.get("/snapshots", summary="Get historical graph snapshots")
async def get_graph_snapshots(
    snapshot_type: str = "daily",
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get periodic snapshots of graph metrics over time."""
    snapshots = (
        db.query(models.HistoricalGraphSnapshot)
        .filter(models.HistoricalGraphSnapshot.snapshot_type == snapshot_type)
        .order_by(desc(models.HistoricalGraphSnapshot.snapshot_date))
        .limit(limit)
        .all()
    )

    return [
        {
            "id": s.id,
            "snapshot_date": str(s.snapshot_date),
            "snapshot_type": s.snapshot_type,
            "total_masters": s.total_masters,
            "total_offers": s.total_offers,
            "total_relationships": s.total_relationships,
            "duplicate_rate": s.duplicate_rate,
            "avg_confidence": s.avg_confidence,
            "avg_completeness": s.avg_completeness,
        }
        for s in snapshots
    ]


@router.post("/snapshots/take", summary="Take a historical graph snapshot")
async def take_graph_snapshot(
    snapshot_type: str = "daily",
    db: Session = Depends(get_db),
):
    """Generates and stores a new historical graph snapshot."""
    metrics = kg_service.compute_graph_metrics(db)

    avg_completeness = db.query(func.avg(models.MasterProduct.completeness_score)).filter(
        models.MasterProduct.is_active == True
    ).scalar() or 0.0

    snapshot = models.HistoricalGraphSnapshot(
        snapshot_type=snapshot_type,
        total_masters=metrics["total_masters"],
        total_offers=metrics["total_offers"],
        total_relationships=metrics["total_relationships"],
        total_attributes=metrics["total_attributes"],
        duplicate_rate=metrics["duplicate_detection_rate"],
        avg_confidence=metrics["avg_confidence"],
        avg_completeness=round(avg_completeness, 1),
        avg_offer_freshness=1.0,
        metrics_json=metrics,
    )
    db.add(snapshot)
    db.commit()

    return {"status": "success", "snapshot_id": snapshot.id, "type": snapshot_type}


# ─── Phase 2: Enterprise Matching Engine Admin Endpoints ─────────────

@router.get("/matching/metrics", summary="Matching Engine Analytics & Accuracy Metrics")
async def get_matching_metrics(db: Session = Depends(get_db)):
    """Returns engine throughput, accuracy, auto-match rates, and feedback stats."""
    from matching_engine.matching_metrics import matching_metrics_collector
    return matching_metrics_collector.get_summary(db=db)


@router.get("/matching/history", summary="Query Matching Decision Logs")
async def get_matching_history(
    decision: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Query immutable matching decision logs with filter and pagination."""
    q = db.query(models.MatchingHistoryLog)
    if decision:
        q = q.filter(models.MatchingHistoryLog.decision == decision)

    total = q.count()
    offset = (page - 1) * page_size
    logs = q.order_by(desc(models.MatchingHistoryLog.created_at)).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "logs": [
            {
                "id": l.id,
                "listing_title": l.listing_title,
                "marketplace": l.marketplace,
                "candidates_evaluated_count": l.candidates_evaluated_count,
                "winning_candidate_id": l.winning_candidate_id,
                "decision": l.decision,
                "confidence_score": l.confidence_score,
                "execution_time_ms": l.execution_time_ms,
                "fallback_used": l.fallback_used,
                "created_at": str(l.created_at),
            }
            for l in logs
        ],
    }


@router.get("/matching/explain/{history_id}", summary="Get Machine/Human-Readable Decision Breakdown")
async def explain_matching_decision(history_id: int, db: Session = Depends(get_db)):
    """Returns detailed explainability breakdown for a specific decision log."""
    log_entry = db.query(models.MatchingHistoryLog).filter(models.MatchingHistoryLog.id == history_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Matching history log entry not found")

    return {
        "id": log_entry.id,
        "listing_title": log_entry.listing_title,
        "marketplace": log_entry.marketplace,
        "decision": log_entry.decision,
        "confidence_score": log_entry.confidence_score,
        "winning_candidate_id": log_entry.winning_candidate_id,
        "embedding_model_version": log_entry.embedding_model_version,
        "algorithm_version": log_entry.algorithm_version,
        "execution_time_ms": log_entry.execution_time_ms,
        "explainability": log_entry.explainability_json,
        "signal_breakdown": log_entry.signal_breakdown_json,
    }


@router.get("/matching/feedback", summary="List Continuous Learning Feedback Dataset")
async def get_matching_feedback(
    feedback_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Query reviewer feedback records for continuous learning dataset."""
    from matching_engine.training_feedback import training_feedback_repo
    return training_feedback_repo.get_feedback_dataset(feedback_type=feedback_type, limit=limit, db=db)


@router.post("/matching/feedback", summary="Record Reviewer Decision Feedback")
async def record_matching_feedback(
    feedback_type: str,  # approved_match, rejected_match, false_positive, false_negative, manual_correction
    master_product_id: Optional[int] = None,
    offer_id: Optional[int] = None,
    candidate_master_id: Optional[int] = None,
    reviewer_id: int = 1,
    decision_notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Record manual reviewer feedback for continuous learning."""
    from matching_engine.training_feedback import training_feedback_repo
    feedback = training_feedback_repo.record_feedback(
        feedback_type=feedback_type,
        master_product_id=master_product_id,
        offer_id=offer_id,
        candidate_master_id=candidate_master_id,
        reviewer_id=reviewer_id,
        decision_notes=decision_notes,
        db=db,
    )
    db.commit()
    return {"status": "success", "feedback_id": feedback.id}


@router.get("/matching/config", summary="Get Engine Weights & Threshold Configuration")
async def get_matching_config():
    """Returns active ensemble signal weights and category thresholds."""
    from matching_engine.matching_config import SIGNAL_WEIGHTS, CATEGORY_THRESHOLDS, THRESHOLD_AUTO_MATCH, THRESHOLD_REVIEW_QUEUE
    return {
        "auto_match_threshold": THRESHOLD_AUTO_MATCH,
        "review_queue_threshold": THRESHOLD_REVIEW_QUEUE,
        "category_thresholds": CATEGORY_THRESHOLDS,
        "signal_weights": SIGNAL_WEIGHTS,
    }
