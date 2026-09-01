"""
Brand Battle — Session Manager
Tracks active device sessions, user agents, IP addresses, and concurrent logouts.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any
from auth.schemas import DeviceSession


class SessionManager:
    """Manages active user device sessions."""

    def __init__(self):
        self._sessions: Dict[int, List[DeviceSession]] = {}

    def create_session(
        self,
        user_id: int,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0)",
        ip_address: str = "127.0.0.1",
        country: str = "India"
    ) -> DeviceSession:
        device_type = "Mobile" if "Mobile" in user_agent else "Desktop"
        session_id = f"sess_{uuid.uuid4().hex[:8]}"

        session = DeviceSession(
            session_id=session_id,
            user_agent=user_agent,
            device_type=device_type,
            ip_address=ip_address,
            country=country,
            last_active=datetime.now(timezone.utc),
            is_current=True
        )

        if user_id not in self._sessions:
            self._sessions[user_id] = []
        self._sessions[user_id].append(session)
        return session

    def list_user_sessions(self, user_id: int) -> List[DeviceSession]:
        return self._sessions.get(user_id, [])

    def revoke_other_sessions(self, user_id: int, current_session_id: str) -> int:
        if user_id in self._sessions:
            initial_count = len(self._sessions[user_id])
            self._sessions[user_id] = [s for s in self._sessions[user_id] if s.session_id == current_session_id]
            return initial_count - len(self._sessions[user_id])
        return 0


session_manager = SessionManager()
