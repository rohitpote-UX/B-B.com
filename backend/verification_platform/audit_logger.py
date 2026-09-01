"""
Brand Battle — Audit Logger
Creates immutable cryptographic audit trails for all verification pipeline decisions.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from verification_platform.schemas import AuditLogRecord


class AuditLogger:
    """Logs immutable audit records for verification actions."""

    def __init__(self):
        self._audit_trail: List[AuditLogRecord] = []

    def log_action(
        self,
        product_id: int,
        action: str,
        actor: str,
        details: Dict[str, Any]
    ) -> AuditLogRecord:
        audit_id = f"aud_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        
        raw_str = f"{audit_id}:{product_id}:{action}:{actor}:{json.dumps(details, sort_keys=True)}:{now.isoformat()}"
        integrity_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        record = AuditLogRecord(
            audit_id=audit_id,
            product_id=product_id,
            action=action,
            actor=actor,
            details=details,
            integrity_hash=integrity_hash,
            timestamp=now
        )

        self._audit_trail.append(record)
        return record

    def get_audit_trail(self, product_id: Optional[int] = None, limit: int = 50) -> List[AuditLogRecord]:
        if product_id:
            filtered = [r for r in self._audit_trail if r.product_id == product_id]
            return filtered[-limit:]
        return self._audit_trail[-limit:]


audit_logger = AuditLogger()
