"""
Brand Battle — 6. Conversion Tracking Engine
Logs order IDs, transaction IDs, sale amounts, and commissions.
"""

import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from affiliate_platform.repository import affiliate_repo


class ConversionTrackerEngine:
    """Tracks affiliate conversions and order commission records."""

    def record_conversion(
        self,
        db: Session,
        provider_key: str,
        sale_amount: float,
        commission_amount: float,
        order_id: Optional[str] = None,
        click_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record affiliate conversion transaction."""
        conv_id = f"cnv_{uuid.uuid4().hex[:12]}"
        rec = affiliate_repo.record_conversion(
            db=db,
            conversion_id=conv_id,
            provider_key=provider_key,
            sale_amount=sale_amount,
            commission_amount=commission_amount,
            order_id=order_id,
            click_id=click_id,
        )

        return {
            "conversion_id": conv_id,
            "provider_key": provider_key,
            "sale_amount_inr": sale_amount,
            "commission_amount_inr": commission_amount,
            "status": "approved",
        }


# Singleton
conversion_tracker_engine = ConversionTrackerEngine()
