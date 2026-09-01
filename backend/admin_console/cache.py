"""
Brand Battle — Admin Console Redis Cache Layer
Redis caching for Executive Brief snapshots, dashboard metrics (<2s load SLO), and command palette lookups.
"""

from typing import Any, Optional, Dict
from redis_client import get_cache, set_cache, delete_cache
from admin_console.config import admin_config

_PREFIX_BRIEF = "admin:brief:latest"
_PREFIX_OVERVIEW = "admin:overview:snapshot"


class AdminConsoleCache:
    """Redis cache manager targeting <2s dashboard load and <50ms command palette."""

    def get_morning_brief(self) -> Optional[Any]:
        if not admin_config.enable_morning_brief:
            return None
        return get_cache(_PREFIX_BRIEF)

    def set_morning_brief(self, brief_data: Any) -> bool:
        if not admin_config.enable_morning_brief:
            return False
        return set_cache(_PREFIX_BRIEF, brief_data, ttl=3600 * 12)  # 12-hour cache

    def get_overview_snapshot(self) -> Optional[Any]:
        return get_cache(_PREFIX_OVERVIEW)

    def set_overview_snapshot(self, snapshot: Any) -> bool:
        return set_cache(_PREFIX_OVERVIEW, snapshot, ttl=1800)


# Singleton
admin_cache = AdminConsoleCache()
