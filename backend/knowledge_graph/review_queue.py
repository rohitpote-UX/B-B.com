"""
Brand Battle - Intelligent Manual Review Queue Engine
Manages low-confidence match routing, duplicate verification queueing,
and admin review decision workflows (Approve, Reject, Merge, Split, Reprocess).
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

import models
from knowledge_graph.observability import log_audit_event

logger = logging.getLogger("brandbattle.kg.review")


class ReviewQueueEngine:
    """Routes uncertain matches and manages human-in-the-loop decisions."""

    def queue_for_review(
        self,
        trigger_reason: str,
        confidence_score: float,
        payload: Dict[str, Any],
        master_id: Optional[int] = None,
        offer_id: Optional[int] = None,
        priority: str = "medium",
        db: Session = None,
    ) -> models.ReviewQueueItem:
        """
        Creates a ReviewQueueItem for admin review when matching confidence is low or uncertain.
        """
        item = models.ReviewQueueItem(
            master_product_id=master_id,
            offer_id=offer_id,
            trigger_reason=trigger_reason,
            priority=priority,
            status=models.ReviewQueueStatus.PENDING.value,
            confidence_score=confidence_score,
            metadata_json=payload,
            created_at=datetime.now(timezone.utc),
        )
        db.add(item)
        db.flush()

        log_audit_event(
            db=db,
            entity_type="review_queue_item",
            entity_id=item.id,
            action=models.AuditEventType.REVIEW_TRIGGERED.value,
            new_value={"reason": trigger_reason, "confidence": confidence_score},
            reason=f"Review queued: {trigger_reason}"
        )

        logger.info(f"📋 Queued Review Item #{item.id} [Reason: {trigger_reason}, Conf: {confidence_score:.3f}]")
        return item

    def process_decision(
        self,
        queue_item_id: int,
        action: str,  # approve, reject, merge, split, reprocess
        reviewer_id: int,
        notes: Optional[str] = None,
        target_master_id: Optional[int] = None,
        db: Session = None,
    ) -> Tuple[bool, str]:
        """Processes an admin decision on a ReviewQueueItem."""
        item = db.query(models.ReviewQueueItem).filter(models.ReviewQueueItem.id == queue_item_id).first()
        if not item:
            return False, "Review queue item not found"

        if item.status != models.ReviewQueueStatus.PENDING.value:
            return False, f"Item is already processed (Status: {item.status})"

        action_lower = action.lower()
        if action_lower == "approve":
            item.status = models.ReviewQueueStatus.APPROVED.value
            if item.master_product_id:
                master = db.query(models.MasterProduct).filter(models.MasterProduct.id == item.master_product_id).first()
                if master:
                    master.is_verified = True
        elif action_lower == "reject":
            item.status = models.ReviewQueueStatus.REJECTED.value
        elif action_lower == "merge" and target_master_id and item.master_product_id:
            from knowledge_graph.kg_service import kg_service
            kg_service.merge_masters(item.master_product_id, target_master_id, db)
            item.status = models.ReviewQueueStatus.MERGED.value
        elif action_lower == "split":
            item.status = models.ReviewQueueStatus.SPLIT.value
        elif action_lower == "reprocess":
            item.status = models.ReviewQueueStatus.PENDING.value
        else:
            return False, f"Invalid decision action '{action}'"

        item.reviewer_id = reviewer_id
        item.decision_notes = notes
        item.reviewed_at = datetime.now(timezone.utc)

        log_audit_event(
            db=db,
            entity_type="review_queue_item",
            entity_id=item.id,
            action=models.AuditEventType.REVIEW_DECIDED.value,
            previous_value={"status": "pending"},
            new_value={"status": item.status, "action": action_lower},
            reason=notes or f"Admin decision: {action_lower}",
            actor=f"user_{reviewer_id}"
        )

        db.flush()
        return True, f"Decision '{action_lower}' recorded for review item #{queue_item_id}"


review_queue_engine = ReviewQueueEngine()
