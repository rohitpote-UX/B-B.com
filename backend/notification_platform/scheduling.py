"""
Brand Battle — 2. Smart Timing Engine
Schedules notifications for user active windows (morning routine, lunch break, evening browsing, weekend shopping).
"""

from typing import Dict, Any
from datetime import datetime, timezone


class SmartTimingEngine:
    """Determines optimal delivery window based on user routines."""

    def determine_optimal_time(self, user_id: int) -> Dict[str, Any]:
        """Detect current user time slot and delivery suitability."""
        now = datetime.now(timezone.utc)
        hour = now.hour

        if 8 <= hour < 10:
            slot = "morning_routine"
            suitable = True
        elif 12 <= hour < 14:
            slot = "lunch_break"
            suitable = True
        elif 18 <= hour < 21:
            slot = "evening_browsing"
            suitable = True
        elif 10 <= hour < 12 or 14 <= hour < 18:
            slot = "work_hours"
            suitable = False  # Avoid interrupting work unless critical
        else:
            slot = "late_night"
            suitable = False

        return {
            "time_slot": slot,
            "is_suitable_now": suitable,
            "recommended_hour": 19,  # Default 7:00 PM evening slot
        }


# Singleton
smart_timing_engine = SmartTimingEngine()
