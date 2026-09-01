"""
Brand Battle — Enterprise Affiliate Commerce Platform Configuration
Settings, provider defaults, latency targets (<50ms deep link generation), and routing rules.
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class AffiliateSLOs(BaseModel):
    """Performance targets (milliseconds)."""
    deeplink_generation_ms: int = 50
    click_logging_async_ms: int = 10
    provider_failover_ms: int = 20


class AffiliatePlatformConfig(BaseModel):
    """Master configuration for the Affiliate Platform."""
    enabled: bool = True
    version: str = "v11.0-enterprise-affiliate-platform"
    slo: AffiliateSLOs = AffiliateSLOs()

    # Feature flags
    enable_multi_network_routing: bool = True
    enable_fraud_detection: bool = True
    enable_fallback: bool = True
    enable_link_health_checks: bool = True

    # Default affiliate parameters
    amazon_tag: str = "brandbattle-21"
    flipkart_tag: str = "brandbattle"
    impact_subid: str = "bb_campaign"


affiliate_config = AffiliatePlatformConfig()
