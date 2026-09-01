"""
Brand Battle — Trigger Engine
Processes raw events and evaluates delivery pipeline.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Product


class TriggerEngine:
    """Evaluates raw triggers into candidate notification events."""

    def process_trigger(
        self, db: Session, user_id: int, event_type: str, product: Optional[Product] = None
    ) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "event_type": event_type,
            "product_id": product.id if product else None,
            "status": "processed",
        }


# Singleton
trigger_engine = TriggerEngine()
