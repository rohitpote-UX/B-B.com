"""
Brand Battle — 11. Celebration Engine
Celebrates user savings milestones ("You've saved ₹12,450 using Brand Battle").
"""

from typing import Dict, Any


class CelebrationEngine:
    """Calculates user savings milestones and rewards smart decisions."""

    def celebrate_milestone(self, user_name: str, total_saved_inr: float) -> Dict[str, Any]:
        """Format celebration notification."""
        return {
            "title": f"🎉 Milestone Unlocked, {user_name}!",
            "body": f"You've saved a total of ₹{total_saved_inr:,.0f} by making smart purchase decisions on Brand Battle!",
            "total_saved": total_saved_inr,
        }


# Singleton
celebration_engine = CelebrationEngine()
