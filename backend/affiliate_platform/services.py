"""
Brand Battle — Enterprise Affiliate Commerce Platform Service Facade
High-level service facade orchestrating deep link generation, routing, click tracking, conversions, and disclosures.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from affiliate_platform.deeplink_generator import deeplink_generator
from affiliate_platform.affiliate_engine import multi_network_routing_engine
from affiliate_platform.click_tracker import click_tracker_engine
from affiliate_platform.conversion_tracker import conversion_tracker_engine
from affiliate_platform.analytics import commission_analytics_engine
from affiliate_platform.repository import affiliate_repo
from affiliate_platform.schemas import DeepLinkResponseSchema, CommissionDashboardSchema

logger = logging.getLogger("brandbattle.affiliate_platform.service")


class AffiliatePlatformService:
    """Master service facade for the Affiliate Commerce Platform."""

    def generate_product_deeplink(
        self,
        db: Session,
        product_id: int,
        destination_url: str,
        marketplace_name: str = "Amazon",
        touchpoint: str = "search",
        session_id: str = "guest_session",
    ) -> DeepLinkResponseSchema:
        """Generate affiliate deep link targeting <50ms latency."""
        provider_key = multi_network_routing_engine.select_best_provider(destination_url)
        res = deeplink_generator.generate_deeplink(
            product_id=product_id,
            destination_url=destination_url,
            provider_key=provider_key,
            session_id=session_id,
        )

        affiliate_repo.record_link(
            db=db,
            link_token=res.link_token,
            product_id=product_id,
            provider_key=res.provider_key,
            destination_url=destination_url,
            affiliate_url=res.affiliate_url,
        )

        return res

    def get_user_disclosure(self) -> Dict[str, Any]:
        """8. Transparent Disclosure Notice."""
        return {
            "notice": (
                "If you purchase through this link, Brand Battle may earn an affiliate commission at no additional cost to you. "
                "Our AI recommendations, search rankings, and price evaluations remain 100% independent, objective, and data-driven."
            ),
            "is_active": True,
        }

    def get_commission_dashboard(self, db: Session) -> CommissionDashboardSchema:
        """Fetch commission dashboard metrics."""
        return commission_analytics_engine.get_commission_dashboard(db)


# Singleton
affiliate_platform_service = AffiliatePlatformService()
