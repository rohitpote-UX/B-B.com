"""
Brand Battle — Enterprise Admin Console Service Facade
High-level service facade unifying all 20 Admin Console modules, Executive Brief, Copilot, and Command Palette.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from admin_console.overview_dashboard import executive_overview_engine
from admin_console.executive_brief import executive_brief_engine
from admin_console.ai_copilot import admin_ai_copilot
from admin_console.command_palette import command_palette_engine
from admin_console.review_queue import unified_review_queue_engine
from admin_console.feature_flags import feature_flag_center_engine
from admin_console.ai_ops_center import ai_ops_center_engine
from admin_console.audit_compliance import audit_compliance_engine

logger = logging.getLogger("brandbattle.admin_console.service")


class AdminConsoleService:
    """Master service facade orchestrating Enterprise Admin Command Center operations."""

    def get_overview_dashboard(self, db: Session) -> Dict[str, Any]:
        """Fetch Executive Overview Dashboard."""
        return executive_overview_engine.get_overview_metrics(db)

    def get_executive_brief(self, db: Session) -> Dict[str, Any]:
        """Fetch Executive Morning Brief."""
        brief = executive_brief_engine.generate_morning_brief(db)
        return brief.model_dump()

    def query_copilot(self, db: Session, prompt: str) -> Dict[str, Any]:
        """Process AI Admin Copilot query."""
        resp = admin_ai_copilot.process_query(db, prompt)
        return resp.model_dump()

    def search_command_palette(self, query: str = "") -> List[Dict[str, Any]]:
        """Search Command Palette quick actions."""
        return command_palette_engine.search_commands(query)

    def get_review_queue(self, db: Session) -> Dict[str, Any]:
        """Fetch Unified Review Queue items."""
        return unified_review_queue_engine.get_review_queue_summary(db)

    def get_feature_flags(self, db: Session) -> List[Dict[str, Any]]:
        """Fetch Feature Flags."""
        return feature_flag_center_engine.get_feature_flags(db)

    def get_ai_ops_center(self, db: Session) -> Dict[str, Any]:
        """Fetch AI Operations Center health metrics."""
        return ai_ops_center_engine.get_ai_subsystems_health(db)

    def get_audit_trail(self, db: Session) -> Dict[str, Any]:
        """Fetch Audit & Compliance logs."""
        return audit_compliance_engine.get_audit_trail_summary(db)


# Singleton
admin_console_service = AdminConsoleService()
