"""
Brand Battle — 16. User & Role Management (RBAC) Engine
Manages granular RBAC permissions across roles (SuperAdmin, Operations, DataSteward, AIReviewer, Support, Analyst, Auditor).
"""

from typing import Dict, Any, List
from admin_console.config import admin_config


class UserRBACEngine:
    """Manages RBAC permission matrices for admin roles."""

    def get_rbac_matrix(self) -> Dict[str, Any]:
        return {
            "roles": [
                admin_config.roles.super_admin,
                admin_config.roles.operations,
                admin_config.roles.data_steward,
                admin_config.roles.ai_reviewer,
                admin_config.roles.support,
                admin_config.roles.analyst,
                admin_config.roles.auditor,
            ],
            "permissions_count": 28,
        }


# Singleton
user_rbac_engine = UserRBACEngine()
