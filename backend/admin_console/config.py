"""
Brand Battle — Enterprise Command Center (Admin Console) Configuration
Settings, RBAC role definitions, audit retention, and performance SLOs (<2s dashboard load, <50ms command palette).
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class AdminSLOs(BaseModel):
    """Performance targets (milliseconds)."""
    dashboard_load_ms: int = 2000
    widget_refresh_ms: int = 500
    global_search_ms: int = 100
    command_palette_ms: int = 50


class RBACRoles(BaseModel):
    """Supported RBAC Roles."""
    super_admin: str = "Super Admin"
    operations: str = "Operations"
    data_steward: str = "Data Steward"
    ai_reviewer: str = "AI Reviewer"
    support: str = "Support"
    analyst: str = "Analyst"
    auditor: str = "Read-only Auditor"


class AdminConsoleConfig(BaseModel):
    """Master configuration for the Admin Console Platform."""
    enabled: bool = True
    version: str = "v8.0.0-enterprise-command-center"
    slo: AdminSLOs = AdminSLOs()
    roles: RBACRoles = RBACRoles()

    # Feature flags
    enable_morning_brief: bool = True
    enable_ai_copilot: bool = True
    enable_command_palette: bool = True
    enable_review_queue: bool = True
    enable_feature_flags: bool = True


admin_config = AdminConsoleConfig()
