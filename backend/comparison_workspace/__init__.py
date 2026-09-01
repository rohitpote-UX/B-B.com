"""
Brand Battle — Enterprise Comparison Workspace Package
Exports router, service, and workspace singletons.
"""

from comparison_workspace.routers import router as comparison_workspace_router
from comparison_workspace.services import comparison_workspace_service
from comparison_workspace.config import workspace_config

__all__ = [
    "comparison_workspace_router",
    "comparison_workspace_service",
    "workspace_config",
]
