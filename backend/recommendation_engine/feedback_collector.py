"""
Brand Battle — Recommendation Feedback & Continuous Learning Collector
Collects implicit and explicit feedback signals (clicked, compared, wishlisted, purchased, ignored) to tune future recommendation models.
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
from logging_config import logger


class FeedbackCollector:
    """Collects behavioral feedback events for continuous learning."""

    def __init__(self):
        self._feedback_events: List[Dict[str, Any]] = []
        self._feedback_weights = defaultdict(lambda: {"positive": 0, "negative": 0})

    def record_feedback(
        self, 
        recommendation_id: str, 
        product_id: int, 
        action: str,  # clicked, compared, wishlisted, purchased, ignored, rejected
        user_id: Optional[int] = None
    ):
        """Record user feedback action on a recommendation item."""
        try:
            event = {
                "recommendation_id": recommendation_id,
                "product_id": product_id,
                "action": action,
                "user_id": user_id
            }
            self._feedback_events.append(event)
            
            if action in ["clicked", "compared", "wishlisted", "purchased"]:
                self._feedback_weights[product_id]["positive"] += 1
            elif action in ["ignored", "rejected"]:
                self._feedback_weights[product_id]["negative"] += 1

            if len(self._feedback_events) > 5000:
                self._feedback_events = self._feedback_events[-2000:]
        except Exception as e:
            logger.error(f"Error collecting recommendation feedback: {e}")

    def get_feedback_weights(self, product_id: int) -> Dict[str, int]:
        """Retrieve aggregated feedback counts for a product."""
        return self._feedback_weights.get(product_id, {"positive": 0, "negative": 0})


feedback_collector_service = FeedbackCollector()
