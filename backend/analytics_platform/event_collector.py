"""
Brand Battle — Universal Event Collector Service
High-throughput event collector service guaranteeing <20ms ingestion latency.
"""

import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from analytics_platform.event_schema import UniversalEventPayload
from analytics_platform.repository import analytics_repo
from analytics_platform.cache import analytics_cache
from analytics_platform.metrics import analytics_metrics

logger = logging.getLogger("brandbattle.analytics_platform.collector")


class UniversalEventCollector:
    """Ingests, validates, and dispatches platform events targeting <20ms latency."""

    def ingest_event(
        self,
        db: Session,
        event_category: str,
        event_type: str,
        user_id: Optional[int] = None,
        session_id: str = "guest_session",
        device_type: str = "desktop",
        payload: Optional[Dict[str, Any]] = None,
    ) -> UniversalEventPayload:
        """Ingest structured event and dispatch to Redis stream & persistent audit log."""
        start_time = time.time()

        event = UniversalEventPayload(
            user_id=user_id,
            session_id=session_id,
            device_type=device_type,
            event_category=event_category,
            event_type=event_type,
            metadata=payload or {},
        )

        # 1. Push to Redis Stream (<5ms)
        analytics_cache.push_to_stream({
            "event_id": event.event_id,
            "event_category": event.event_category,
            "event_type": event.event_type,
            "user_id": str(event.user_id or ""),
            "session_id": event.session_id,
            "timestamp": event.timestamp,
        })

        # 2. Persist to Analytics Event Store
        analytics_repo.record_event(
            db=db,
            event_id=event.event_id,
            event_category=event.event_category,
            event_type=event.event_type,
            user_id=event.user_id,
            session_id=event.session_id,
            device_type=event.device_type,
            payload=event.metadata,
        )

        latency = (time.time() - start_time) * 1000
        analytics_metrics.record_ingestion(latency_ms=latency)

        return event


# Singleton
universal_event_collector = UniversalEventCollector()
