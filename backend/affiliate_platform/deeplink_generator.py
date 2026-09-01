"""
Brand Battle — 2. Deep Link Generator
Generates direct retailer affiliate deep links targeting <50ms latency while preserving campaign tracking.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional

from affiliate_platform.provider_registry import provider_registry
from affiliate_platform.schemas import DeepLinkResponseSchema
from affiliate_platform.metrics import affiliate_metrics

logger = logging.getLogger("brandbattle.affiliate_platform.deeplink")


class DeepLinkGenerator:
    """Generates product affiliate deep links targeting <50ms latency."""

    def generate_deeplink(
        self, product_id: int, destination_url: str, provider_key: str = "amazon", session_id: str = "guest_session"
    ) -> DeepLinkResponseSchema:
        """Generate affiliate deep link."""
        start_time = time.time()

        provider = provider_registry.get_provider(provider_key) or provider_registry.get_provider("amazon")
        if provider:
            affiliate_url = provider.generate_affiliate_url(destination_url, campaign_subid=session_id)
            used_key = provider.provider_key
            is_fallback = False
        else:
            affiliate_url = destination_url
            used_key = "direct"
            is_fallback = True

        link_token = f"aff_{uuid.uuid4().hex[:12]}"
        redirect_url = f"/api/affiliate/redirect/{link_token}"

        latency = (time.time() - start_time) * 1000
        affiliate_metrics.record_deeplink_latency(latency)

        return DeepLinkResponseSchema(
            link_token=link_token,
            product_id=product_id,
            provider_key=used_key,
            destination_url=destination_url,
            affiliate_url=affiliate_url,
            redirect_url=redirect_url,
            is_fallback=is_fallback,
        )


# Singleton
deeplink_generator = DeepLinkGenerator()
