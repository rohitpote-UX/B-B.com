"""
Brand Battle — 19. Command Palette Engine
Linear/VS Code style quick action search & execution targeting <50ms response latency.
"""

from typing import List, Dict, Any


class CommandPaletteEngine:
    """Linear/VS Code style command palette index and search engine."""

    COMMANDS = [
        {"id": "cmd_01", "title": "Open Product Operations Center", "category": "Navigation", "action_type": "navigate", "target_url": "/admin/products"},
        {"id": "cmd_02", "title": "View AI Matching Borderline Cases", "category": "Review Queue", "action_type": "navigate", "target_url": "/admin/matching"},
        {"id": "cmd_03", "title": "Open Executive Morning Brief", "category": "Briefings", "action_type": "navigate", "target_url": "/admin/brief"},
        {"id": "cmd_04", "title": "Audit Admin Actions & Logs", "category": "Compliance", "action_type": "navigate", "target_url": "/admin/audit"},
        {"id": "cmd_05", "title": "Manage Feature Flags & Rollouts", "category": "Operations", "action_type": "navigate", "target_url": "/admin/flags"},
        {"id": "cmd_06", "title": "Check Marketplace Scraper Status", "category": "Marketplaces", "action_type": "navigate", "target_url": "/admin/marketplaces"},
    ]

    def search_commands(self, query: str = "") -> List[Dict[str, Any]]:
        """Search commands by keyword targeting <50ms latency."""
        if not query:
            return self.COMMANDS

        q = query.lower().strip()
        filtered = [
            c for c in self.COMMANDS
            if q in c["title"].lower() or q in c["category"].lower()
        ]
        return filtered if filtered else self.COMMANDS[:3]


# Singleton
command_palette_engine = CommandPaletteEngine()
