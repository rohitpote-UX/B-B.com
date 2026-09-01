"""
Brand Battle — Analytics Platform Repository Layer
Database access layer following the Repository Pattern for events, journeys, funnels, and insights.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from analytics_platform.models import (
    AnalyticsEvent, UserSession, UserJourney, FunnelDefinition,
    InsightReport, AnomalyRecord, DashboardSnapshot
)


class AnalyticsRepository:
    """Repository managing data access for the Analytics & Decision Intelligence Platform."""

    def record_event(
        self,
        db: Session,
        event_id: str,
        event_category: str,
        event_type: str,
        user_id: Optional[int] = None,
        session_id: str = "guest_session",
        device_type: str = "desktop",
        payload: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsEvent:
        """Record an immutable analytics event log."""
        event = AnalyticsEvent(
            event_id=event_id,
            event_category=event_category,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            device_type=device_type,
            payload_json=payload,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def get_recent_insights(self, db: Session, limit: int = 10) -> List[InsightReport]:
        """Fetch recent AI Plain-Language Insights."""
        return (
            db.query(InsightReport)
            .order_by(desc(InsightReport.created_at))
            .limit(limit)
            .all()
        )

    def record_insight(
        self,
        db: Session,
        title: str,
        category: str,
        narrative_text: str,
        confidence_score: float = 0.90,
        impact_level: str = "high",
    ) -> InsightReport:
        """Create an AI insight report."""
        report = InsightReport(
            title=title,
            category=category,
            narrative_text=narrative_text,
            confidence_score=confidence_score,
            impact_level=impact_level,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def record_anomaly(
        self,
        db: Session,
        anomaly_type: str,
        subsystem: str,
        description: str,
        severity: str,
        metric_value: float,
        baseline_value: float,
    ) -> AnomalyRecord:
        """Create an anomaly record."""
        anomaly = AnomalyRecord(
            anomaly_type=anomaly_type,
            subsystem=subsystem,
            description=description,
            severity=severity,
            metric_value=metric_value,
            baseline_value=baseline_value,
        )
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        return anomaly

    def get_unresolved_anomalies(self, db: Session) -> List[AnomalyRecord]:
        """Fetch active unresolved anomalies."""
        return (
            db.query(AnomalyRecord)
            .filter(AnomalyRecord.resolved == False)
            .order_by(desc(AnomalyRecord.created_at))
            .all()
        )


# Singleton
analytics_repo = AnalyticsRepository()
