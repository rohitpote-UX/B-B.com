"""
Brand Battle - Training Feedback Repository
Stores human-in-the-loop reviewer decision feedback as continuous learning datasets.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
import logging

import models

logger = logging.getLogger("brandbattle.matching.feedback")


class TrainingFeedbackRepository:
    """Manages continuous learning feedback dataset records for future model tuning."""

    def record_feedback(
        self,
        feedback_type: str,  # approved_match, rejected_match, false_positive, false_negative, manual_correction
        master_product_id: Optional[int] = None,
        offer_id: Optional[int] = None,
        candidate_master_id: Optional[int] = None,
        signal_snapshot: Optional[Dict[str, Any]] = None,
        reviewer_id: Optional[int] = None,
        decision_notes: Optional[str] = None,
        db: Session = None,
    ) -> models.TrainingFeedbackRecord:
        """Stores a reviewer decision feedback entry for model continuous learning."""
        feedback = models.TrainingFeedbackRecord(
            master_product_id=master_product_id,
            offer_id=offer_id,
            candidate_master_id=candidate_master_id,
            feedback_type=feedback_type,
            signal_snapshot_json=signal_snapshot,
            reviewer_id=reviewer_id,
            decision_notes=decision_notes,
            created_at=datetime.now(timezone.utc)
        )
        db.add(feedback)
        db.flush()

        logger.info(f"TrainingFeedback: Recorded '{feedback_type}' feedback [RecordID: {feedback.id}]")
        return feedback

    def get_feedback_dataset(
        self,
        feedback_type: Optional[str] = None,
        limit: int = 100,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Queries training feedback dataset records for model analysis."""
        q = db.query(models.TrainingFeedbackRecord)
        if feedback_type:
            q = q.filter(models.TrainingFeedbackRecord.feedback_type == feedback_type)

        records = q.order_by(desc(models.TrainingFeedbackRecord.created_at)).limit(limit).all()

        return [
            {
                "id": r.id,
                "feedback_type": r.feedback_type,
                "master_product_id": r.master_product_id,
                "offer_id": r.offer_id,
                "candidate_master_id": r.candidate_master_id,
                "signal_snapshot": r.signal_snapshot_json,
                "reviewer_id": r.reviewer_id,
                "decision_notes": r.decision_notes,
                "created_at": str(r.created_at),
            }
            for r in records
        ]


training_feedback_repo = TrainingFeedbackRepository()
