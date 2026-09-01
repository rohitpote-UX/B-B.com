"""
Brand Battle — 7. Festival Intelligence Engine
Detects major shopping events (Prime Day, Black Friday, Cyber Monday, Big Billion Days, Diwali, Christmas, Republic Day) and predicts festival deal opportunities.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone


class FestivalIntelligenceEngine:
    """Detects upcoming shopping festivals and calculates expected discount depth."""

    FESTIVALS = [
        {"name": "Republic Day Sale", "month": 1, "day": 26, "expected_drop_pct": 15.0},
        {"name": "Holi Sale", "month": 3, "day": 20, "expected_drop_pct": 12.0},
        {"name": "Prime Day / Freedom Sale", "month": 7, "day": 15, "expected_drop_pct": 22.0},
        {"name": "Big Billion Days / Great Indian Festival", "month": 10, "day": 10, "expected_drop_pct": 30.0},
        {"name": "Diwali Sale", "month": 11, "day": 1, "expected_drop_pct": 28.0},
        {"name": "Black Friday & Cyber Monday", "month": 11, "day": 27, "expected_drop_pct": 35.0},
        {"name": "Year End & Christmas Sale", "month": 12, "day": 25, "expected_drop_pct": 20.0},
    ]

    def get_upcoming_festival(self) -> Dict[str, Any]:
        """Identify the next major shopping festival event."""
        now = datetime.now(timezone.utc)
        current_month = now.month

        # Find next festival
        next_fest = None
        for fest in self.FESTIVALS:
            if fest["month"] >= current_month:
                next_fest = fest
                break

        if not next_fest:
            next_fest = self.FESTIVALS[0]  # Next year's Republic Day

        return {
            "festival_name": next_fest["name"],
            "expected_drop_pct": next_fest["expected_drop_pct"],
            "target_month": next_fest["month"],
            "is_peak_event": next_fest["expected_drop_pct"] >= 25.0,
        }


# Singleton
festival_engine = FestivalIntelligenceEngine()
