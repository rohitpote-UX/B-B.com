"""
Brand Battle - Matching History Logger Module
Records immutable matching decision logs with full explainability payloads to the database.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

import models

logger = logging.getLogger("brandbattle.matching.history")


class MatchingHistoryLogger:
    """Logs detailed explainable matching execution events to matching_history_logs."""

    def log_decision(
        self,
        listing_title: str,
        marketplace: str,
        candidates_count: int,
        winning_candidate_id: Optional[int],
        decision: str,
        confidence_score: float,
        signal_breakdown: Dict[str, Any],
        explainability: Dict[str, Any],
        execution_time_ms: float,
        fallback_used: bool = False,
        embedding_model_version: str = "tf_idf_v1_ngram",
        algorithm_version: str = "v2.5_hybrid_ensemble",
        db: Session = None
    ) -> models.MatchingHistoryLog:
        """Creates and commits an immutable MatchingHistoryLog entry."""
        log_entry = models.MatchingHistoryLog(
            listing_title=listing_title[:500],
            marketplace=marketplace,
            candidates_evaluated_count=candidates_count,
            winning_candidate_id=winning_candidate_id,
            decision=decision,
            confidence_score=confidence_score,
            signal_breakdown_json=signal_breakdown,
            explainability_json=explainability,
            embedding_model_version=embedding_model_version,
            algorithm_version=algorithm_version,
            execution_time_ms=execution_time_ms,
            fallback_used=fallback_used,
            created_at=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.flush()

        logger.debug(f"MatchingHistory: Logged decision '{decision}' for '{listing_title[:40]}' [LogID: {log_entry.id}]")
        return log_entry


matching_history_logger = MatchingHistoryLogger()
