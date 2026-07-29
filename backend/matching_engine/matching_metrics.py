"""
Brand Battle - Matching Engine Metrics Collector
Tracks matching confidence distribution, auto-match rates, review queue volumes,
execution latency, and fallback frequencies.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import time
import logging

import models

logger = logging.getLogger("brandbattle.matching.metrics")


class MatchingMetricsCollector:
    """Aggregates real-time performance and accuracy metrics for the AI Matching Engine."""

    def __init__(self):
        self.start_time = time.time()
        self.total_evaluations = 0
        self.auto_matches = 0
        self.created_masters = 0
        self.routed_reviews = 0
        self.fallbacks_triggered = 0

    def record_match_attempt(self, decision: str, fallback_used: bool = False):
        """Records an evaluation decision."""
        self.total_evaluations += 1
        if fallback_used:
            self.fallbacks_triggered += 1

        if decision == "auto_matched":
            self.auto_matches += 1
        elif decision == "create_new":
            self.created_masters += 1
        elif decision == "route_review":
            self.routed_reviews += 1

    def get_summary(self, db: Session = None) -> Dict[str, Any]:
        """Returns engine throughput, accuracy, and review queue metrics."""
        summary = {
            "uptime_seconds": round(time.time() - self.start_time, 1),
            "total_evaluations": self.total_evaluations,
            "auto_matches": self.auto_matches,
            "created_masters": self.created_masters,
            "routed_reviews": self.routed_reviews,
            "fallbacks_triggered": self.fallbacks_triggered,
            "auto_match_rate_pct": round((self.auto_matches / max(1, self.total_evaluations)) * 100, 1),
            "review_rate_pct": round((self.routed_reviews / max(1, self.total_evaluations)) * 100, 1),
        }

        if db:
            avg_conf = db.query(func.avg(models.MatchingHistoryLog.confidence_score)).scalar() or 0.0
            avg_latency = db.query(func.avg(models.MatchingHistoryLog.execution_time_ms)).scalar() or 0.0
            total_logged = db.query(func.count(models.MatchingHistoryLog.id)).scalar() or 0
            feedback_count = db.query(func.count(models.TrainingFeedbackRecord.id)).scalar() or 0

            summary.update({
                "db_logged_decisions": total_logged,
                "db_avg_confidence": round(avg_conf, 3),
                "db_avg_latency_ms": round(avg_latency, 2),
                "db_feedback_records": feedback_count,
            })

        return summary


matching_metrics_collector = MatchingMetricsCollector()
