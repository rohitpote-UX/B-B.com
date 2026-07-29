"""
Brand Battle - Review Trigger Module
Automated review queue trigger routing products for human review when matching confidence is uncertain.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from knowledge_graph.review_queue import review_queue_engine

logger = logging.getLogger("brandbattle.matching.review")


class ReviewTrigger:
    """Evaluates whether a decision requires human-in-the-loop review queue placement."""

    def should_trigger_review(self, decision_info: Dict[str, Any]) -> bool:
        """Returns True if the decision indicates review queue placement."""
        return decision_info.get("decision") == "route_review"

    def trigger_review_if_needed(
        self,
        item_features: Dict[str, Any],
        best_candidate: Optional[Dict[str, Any]],
        decision_info: Dict[str, Any],
        explainability: Dict[str, Any],
        db: Session
    ) -> Optional[int]:
        """Queues item for manual review if trigger conditions are met."""
        if not self.should_trigger_review(decision_info):
            return None

        reason = decision_info.get("reason", "Uncertain match confidence")
        confidence = decision_info.get("confidence", 0.0)

        payload = {
            "item_title": item_features.get("clean_title"),
            "marketplace": item_features.get("marketplace"),
            "candidate_id": best_candidate.get("id") if best_candidate else None,
            "candidate_title": best_candidate.get("canonical_name") if best_candidate else None,
            "explainability": explainability,
        }

        item = review_queue_engine.queue_for_review(
            trigger_reason="borderline_match_confidence",
            confidence_score=confidence,
            payload=payload,
            master_id=best_candidate.get("id") if best_candidate else None,
            priority="medium",
            db=db
        )

        logger.info(f"ReviewTrigger: Queued review item #{item.id} [Conf: {confidence:.3f}]")
        return item.id


review_trigger = ReviewTrigger()
