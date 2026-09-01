"""
Brand Battle — Master Notification Pipeline Orchestrator
Executes the AI Decision Pipeline: Value First -> Relevance -> Timing -> Personalization -> Notification.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models import Product, User
from notification_platform.relevance_engine import ai_relevance_engine
from notification_platform.ranking_engine import notification_ranking_engine
from notification_platform.fatigue_detector import fatigue_detector
from notification_platform.quiet_hours import quiet_hours_engine
from notification_platform.preference_center import user_preference_center
from notification_platform.scheduling import smart_timing_engine
from notification_platform.personalization import notification_personalization
from notification_platform.delivery_engine import multi_channel_delivery_engine
from notification_platform.metrics import notification_metrics

logger = logging.getLogger("brandbattle.notification_platform.pipeline")


class MasterNotificationPipelineOrchestrator:
    """Orchestrates the end-to-end Value-First Notification Pipeline."""

    def process_notification_event(
        self,
        db: Session,
        user_id: int,
        event_type: str,
        title: str,
        body: str,
        product: Optional[Product] = None,
        price_drop_pct: float = 0.0,
        opportunity_score: float = 0.0,
        channel: str = "in_app",
    ) -> Dict[str, Any]:
        """Execute Value-First AI Decision Pipeline targeting <100ms decision latency."""
        start_time = time.time()

        # 1. AI Relevance Engine Check
        relevance_score = ai_relevance_engine.calculate_relevance(
            db, user_id, event_type, product, price_drop_pct, opportunity_score
        )
        if not ai_relevance_engine.is_relevant(relevance_score):
            latency = (time.time() - start_time) * 1000
            notification_metrics.record_evaluation(latency_ms=latency, delivered=False, suppressed_reason="low_relevance")
            return {"status": "suppressed", "reason": f"Relevance score {relevance_score} below threshold"}

        # 2. Fatigue Detector Check
        fatigue_status = fatigue_detector.evaluate_fatigue(db, user_id)
        if fatigue_status["should_throttle"] and event_type not in ["price_drop", "buy_now"]:
            latency = (time.time() - start_time) * 1000
            notification_metrics.record_evaluation(latency_ms=latency, delivered=False, suppressed_reason="fatigue_throttled")
            return {"status": "suppressed", "reason": "User fatigue score elevated"}

        # 3. Quiet Hours Check
        if quiet_hours_engine.is_in_quiet_hours(db, user_id) and event_type not in ["price_drop"]:
            latency = (time.time() - start_time) * 1000
            notification_metrics.record_evaluation(latency_ms=latency, delivered=False, suppressed_reason="quiet_hours")
            return {"status": "queued", "reason": "Quiet hours active; queued for morning delivery"}

        # 4. User Preference Center Check
        brand_name = product.brand.name if product and product.brand else None
        if not user_preference_center.is_notification_allowed(db, user_id, channel, brand_name):
            latency = (time.time() - start_time) * 1000
            notification_metrics.record_evaluation(latency_ms=latency, delivered=False, suppressed_reason="preference_filtered")
            return {"status": "suppressed", "reason": "Filtered by user preferences"}

        # 5. Personalization Engine
        content = notification_personalization.personalize_content(db, user_id, title, body)

        # 6. Multi-Channel Delivery Engine
        result = multi_channel_delivery_engine.deliver_notification(
            db=db,
            user_id=user_id,
            notification_type=event_type,
            title=content["title"],
            body=content["body"],
            product_id=product.id if product else None,
            channel=channel,
            relevance_score=relevance_score,
        )

        latency = (time.time() - start_time) * 1000
        notification_metrics.record_evaluation(latency_ms=latency, delivered=True)

        return {"status": "delivered", "data": result}


# Singleton
master_notification_pipeline = MasterNotificationPipelineOrchestrator()
