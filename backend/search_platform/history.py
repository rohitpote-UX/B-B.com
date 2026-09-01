"""
Brand Battle — Search History Logger
Records immutable search logs to the existing SearchHistory table and in-memory audit trail.
"""

import logging
from typing import Dict, Any, Optional, List
from collections import deque
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from models import SearchHistory
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.history")


class SearchHistoryLogger:
    """Immutable search log recorder for analytics and audit."""

    def __init__(self, max_audit_entries: int = 5000):
        self._audit_log: deque = deque(maxlen=max_audit_entries)

    def log_search(
        self,
        db: Session,
        raw_query: str,
        parsed_query: Optional[Dict] = None,
        intent: Optional[str] = None,
        classification: Optional[str] = None,
        filters: Optional[Dict] = None,
        results_count: int = 0,
        latency_ms: float = 0.0,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        was_corrected: bool = False,
        corrected_query: Optional[str] = None,
        algorithm_version: Optional[str] = None,
    ) -> None:
        """Record a search event to DB and in-memory audit log."""
        # 1. Write to existing SearchHistory table
        try:
            filters_json = filters or {}
            if parsed_query:
                filters_json["_parsed"] = parsed_query
            if intent:
                filters_json["_intent"] = intent
            if classification:
                filters_json["_classification"] = classification
            if was_corrected:
                filters_json["_corrected_to"] = corrected_query

            history_entry = SearchHistory(
                user_id=user_id,
                query=raw_query,
                filters=filters_json,
                results_count=results_count,
            )
            db.add(history_entry)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to write search history to DB: {e}")
            try:
                db.rollback()
            except Exception:
                pass

        # 2. Write to in-memory audit log
        audit_entry = {
            "raw_query": raw_query,
            "parsed_query": parsed_query,
            "intent": intent,
            "classification": classification,
            "filters": filters,
            "results_count": results_count,
            "latency_ms": round(latency_ms, 2),
            "user_id": user_id,
            "session_id": session_id,
            "was_corrected": was_corrected,
            "corrected_query": corrected_query,
            "algorithm_version": algorithm_version or search_config.algorithm_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_log.append(audit_entry)

    def get_recent_searches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent search audit log entries."""
        entries = list(self._audit_log)
        entries.reverse()
        return entries[:limit]

    def get_user_history(
        self,
        user_id: int,
        db: Session,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get a user's search history from the database."""
        entries = (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": e.id,
                "query": e.query,
                "filters": e.filters,
                "results_count": e.results_count,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ]


# Singleton
search_history_logger = SearchHistoryLogger()
