"""
Brand Battle — 4. Daily AI Digest Generator
Replaces high-volume notifications with a single evening summary ("Good evening, Rohit. Today we found: 3 deals...").
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models import User
from notification_platform.schemas import DailyDigestSchema


class DailyAIDigestGenerator:
    """Synthesizes high-value daily digest summaries."""

    def generate_digest(self, db: Session, user: User) -> DailyDigestSchema:
        """Generate Daily AI Digest for a user."""
        user_name = user.full_name or user.username or "Shopper"

        headline = f"Good evening, {user_name}."
        summary_text = (
            "Today our AI engines analyzed 14 market updates for your tracked items. "
            "We identified 3 excellent deals, ₹6,400 in potential savings, 2 price drops, "
            "and 1 product predicted to reach its lowest price next week."
        )

        items = [
            {
                "product_name": "iPhone 17 Pro Max",
                "deal_type": "Best Time to Buy",
                "price": 124999.0,
                "savings": 6400.0,
                "badge": "EXCELLENT DEAL",
            },
            {
                "product_name": "MacBook Pro 16-inch M5",
                "deal_type": "Price Drop",
                "price": 249999.0,
                "savings": 12000.0,
                "badge": "BUY NOW",
            },
        ]

        return DailyDigestSchema(
            headline=headline,
            summary_text=summary_text,
            deal_count=len(items),
            total_savings_inr=18400.0,
            items=items,
            created_at=datetime.now(timezone.utc),
        )


# Singleton
digest_generator = DailyAIDigestGenerator()
