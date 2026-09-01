"""
Brand Battle — Enterprise Command Center (Admin Console) Package
Exports router, service, brief engine, copilot engine, and scheduler singletons.
"""

from admin_console.routers import router as admin_console_router
from admin_console.services import admin_console_service
from admin_console.config import admin_config
from admin_console.metrics import admin_metrics
from admin_console.cache import admin_cache
from admin_console.executive_brief import executive_brief_engine
from admin_console.ai_copilot import admin_ai_copilot
from admin_console.command_palette import command_palette_engine
from admin_console.scheduler import admin_scheduler

__all__ = [
    "admin_console_router",
    "admin_console_service",
    "admin_config",
    "admin_metrics",
    "admin_cache",
    "executive_brief_engine",
    "admin_ai_copilot",
    "command_palette_engine",
    "admin_scheduler",
]
