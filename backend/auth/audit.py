"""
Brand Battle — Auth Audit Logger
Logs cryptographic security events, failed login tracking, and anomaly detection.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from auth.schemas import SecurityAuditRecord


class SecurityAuditLogger:
    """Logs security actions and tracks failed login attempt velocity."""

    def __init__(self):
        self._audit_logs: List[SecurityAuditRecord] = []
        self._failed_attempts: Dict[str, int] = {}

    def log_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        ip_address: str = "127.0.0.1",
        device_info: str = "Desktop Browser"
    ) -> SecurityAuditRecord:
        event_id = f"evt_{uuid.uuid4().hex[:8]}"

        record = SecurityAuditRecord(
            event_id=event_id,
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            device_info=device_info,
            timestamp=datetime.now(timezone.utc)
        )

        self._audit_logs.append(record)

        if event_type == "login_failed":
            self._failed_attempts[ip_address] = self._failed_attempts.get(ip_address, 0) + 1
        elif event_type == "login_success":
            self._failed_attempts[ip_address] = 0

        return record

    def is_ip_locked(self, ip_address: str, max_failures: int = 5) -> bool:
        return self._failed_attempts.get(ip_address, 0) >= max_failures


security_audit_logger = SecurityAuditLogger()
