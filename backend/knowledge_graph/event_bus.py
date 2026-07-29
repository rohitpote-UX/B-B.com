"""
Brand Battle - Knowledge Graph Event Bus
Provides an event-driven pub/sub bus for domain events within the Knowledge Graph.
Dispatches events synchronously to registered in-memory handlers and asynchronously
to Redis Streams ('stream:kg_events') when Redis is active.
"""

import json
import time
import uuid
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timezone

from redis_client import redis_client, is_redis_healthy

logger = logging.getLogger("brandbattle.kg.events")

STREAM_KG_EVENTS = "stream:kg_events"


class DomainEvent:
    """Base class for all Knowledge Graph domain events."""

    def __init__(
        self,
        event_type: str,
        entity_id: int,
        payload: Dict[str, Any],
        actor: str = "system",
        correlation_id: Optional[str] = None
    ):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.entity_id = entity_id
        self.payload = payload
        self.actor = actor
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "entity_id": self.entity_id,
            "payload": self.payload,
            "actor": self.actor,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
        }


class EventBus:
    """Central domain event publisher and handler registry."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable[[DomainEvent], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Register a handler callback for a specific domain event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler {handler.__name__} to event '{event_type}'")

    def publish(
        self,
        event_type: str,
        entity_id: int,
        payload: Dict[str, Any],
        actor: str = "system",
        correlation_id: Optional[str] = None
    ) -> DomainEvent:
        """Publishes a domain event to registered handlers and Redis Stream."""
        event = DomainEvent(
            event_type=event_type,
            entity_id=entity_id,
            payload=payload,
            actor=actor,
            correlation_id=correlation_id
        )

        # 1. Dispatch synchronously to in-memory subscribers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__} for '{event_type}': {e}")

        # 2. Publish to Redis Stream for external consumers
        if is_redis_healthy():
            try:
                redis_client.xadd(
                    STREAM_KG_EVENTS,
                    {"event_data": json.dumps(event.to_dict(), default=str)},
                    maxlen=10000
                )
            except Exception as e:
                logger.error(f"Failed to publish event to Redis Stream '{STREAM_KG_EVENTS}': {e}")

        logger.info(f"📢 Published Event '{event_type}' [Entity: {entity_id}, CorID: {event.correlation_id}]")
        return event


# Global event bus singleton instance
event_bus = EventBus()
