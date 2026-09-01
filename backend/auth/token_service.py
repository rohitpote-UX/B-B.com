"""
Brand Battle — Token Service
Manages active sessions, token revocation, and JWT blacklisting.
"""

from typing import Set
from datetime import datetime, timezone

REVOKED_TOKENS: Set[str] = set()


class TokenService:
    """Manages active session revocation and blacklisting."""

    def revoke_token(self, token: str) -> bool:
        REVOKED_TOKENS.add(token)
        return True

    def is_token_revoked(self, token: str) -> bool:
        return token in REVOKED_TOKENS


token_service = TokenService()
