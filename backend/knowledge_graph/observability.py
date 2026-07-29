"""
Brand Battle - Knowledge Graph Observability & Audit Logger
Provides structured logging with correlation IDs, latency tracking decorators,
and immutable graph audit event logging.
"""

import time
import uuid
import functools
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

import models

logger = logging.getLogger("brandbattle.kg.audit")


def get_correlation_id() -> str:
    """Generates or retrieves a correlation ID for request tracing."""
    return str(uuid.uuid4())


def trace_kg_operation(operation_name: str):
    """
    Decorator to measure execution time, track errors, and log structured metrics
    for Knowledge Graph operations.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            cor_id = kwargs.get("correlation_id") or get_correlation_id()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = round((time.time() - start) * 1000, 2)
                logger.info(
                    f"⏱️ KG Trace [{operation_name}] completed in {elapsed_ms}ms "
                    f"[CorID: {cor_id}]"
                )
                return result
            except Exception as e:
                elapsed_ms = round((time.time() - start) * 1000, 2)
                logger.error(
                    f"❌ KG Trace [{operation_name}] FAILED after {elapsed_ms}ms: {e} "
                    f"[CorID: {cor_id}]"
                )
                raise e
        return wrapper
    return decorator


def log_audit_event(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    previous_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    actor: str = "system",
    correlation_id: Optional[str] = None,
) -> models.GraphAuditEvent:
    """
    Creates an immutable audit event record in graph_audit_events table.
    """
    audit_event = models.GraphAuditEvent(
        event_id=str(uuid.uuid4()),
        correlation_id=correlation_id or get_correlation_id(),
        actor=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        previous_value=previous_value,
        new_value=new_value,
        reason=reason,
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit_event)
    db.flush()
    logger.info(
        f"📝 Audit Event: {action.upper()} on {entity_type}:{entity_id} "
        f"by {actor} [EventID: {audit_event.event_id}]"
    )
    return audit_event
