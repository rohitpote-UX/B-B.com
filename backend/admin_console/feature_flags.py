"""
Brand Battle — 17. Feature Flag Center Engine
Manages percentage rollouts, feature toggles, and instant rollback.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from admin_console.repository import admin_repo


class FeatureFlagCenterEngine:
    """Manages feature flag rollouts and instant rollbacks."""

    DEFAULT_FLAGS = [
        {"key": "search_semantic_v2", "name": "Semantic Vector Search v2", "is_enabled": True, "rollout_percentage": 100.0, "subsystem": "search"},
        {"key": "recommendation_hybrid_graph", "name": "Hybrid Graph Recommendation Model", "is_enabled": True, "rollout_percentage": 100.0, "subsystem": "recommendations"},
        {"key": "price_intelligence_forecast_v5", "name": "Price Forecast Intelligence v5", "is_enabled": True, "rollout_percentage": 100.0, "subsystem": "pricing"},
        {"key": "notification_daily_digest", "name": "Daily AI Digest Generator", "is_enabled": True, "rollout_percentage": 100.0, "subsystem": "notifications"},
    ]

    def get_feature_flags(self, db: Session) -> List[Dict[str, Any]]:
        flags = admin_repo.get_feature_flags(db)
        if flags:
            return [
                {
                    "key": f.key,
                    "name": f.name,
                    "is_enabled": f.is_enabled,
                    "rollout_percentage": f.rollout_percentage,
                    "subsystem": f.subsystem,
                }
                for f in flags
            ]
        return self.DEFAULT_FLAGS

    def update_flag(
        self, db: Session, key: str, is_enabled: bool, rollout_pct: float = 100.0
    ) -> Dict[str, Any]:
        flag = admin_repo.update_feature_flag(db, key, is_enabled, rollout_pct)
        return {
            "key": flag.key,
            "is_enabled": flag.is_enabled,
            "rollout_percentage": flag.rollout_percentage,
        }


# Singleton
feature_flag_center_engine = FeatureFlagCenterEngine()
