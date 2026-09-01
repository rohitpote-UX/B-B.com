"""
Brand Battle — Recommendation History Engine
Records immutable audit logs of generated recommendation instances for compliance, debugging, and continuous training.
"""

from typing import List, Dict, Any, Optional
import datetime
from sqlalchemy.orm import Session
from logging_config import logger


class RecommendationHistory:
    """Immutable audit trail logger for recommendation generation events."""

    def __init__(self):
        self._history_log: List[Dict[str, Any]] = []

    def log_recommendation_generation(
        self, 
        source_product_id: Optional[int], 
        rec_type: str, 
        recommended_items: List[Dict[str, Any]], 
        algorithm_version: str,
        user_id: Optional[int] = None
    ):
        """Append immutable record of recommendation generation."""
        try:
            record = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "source_product_id": source_product_id,
                "recommendation_type": rec_type,
                "algorithm_version": algorithm_version,
                "user_id": user_id,
                "total_items": len(recommended_items),
                "items_summary": [
                    {
                        "product_id": item["product"].id if hasattr(item.get("product"), "id") else item.get("product_id"),
                        "ranking_score": item.get("ranking_score", 0.0),
                        "confidence": item.get("confidence", 0.0),
                        "reason": item.get("reason", "")
                    }
                    for item in recommended_items[:5]
                ]
            }
            self._history_log.append(record)
            if len(self._history_log) > 2000:
                self._history_log = self._history_log[-1000:]
        except Exception as e:
            logger.error(f"Error recording recommendation history: {e}")

    def get_recent_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent recommendation generation audit records."""
        return self._history_log[-limit:]


recommendation_history_logger = RecommendationHistory()
