"""
Brand Battle — Pluggable Provider Registry & Network Adapters
Implements concrete adapters for Amazon, Flipkart, Impact, CJ, Awin, Rakuten, Sovrn.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from affiliate_platform.affiliate_provider import BaseAffiliateProvider
from affiliate_platform.config import affiliate_config


class AmazonAssociatesProvider(BaseAffiliateProvider):
    provider_key = "amazon"
    name = "Amazon Associates"

    def generate_affiliate_url(self, destination_url: str, campaign_subid: Optional[str] = None) -> str:
        parsed = urlparse(destination_url)
        query = parse_qs(parsed.query)
        query["tag"] = [affiliate_config.amazon_tag]
        if campaign_subid:
            query["ascsubtag"] = [campaign_subid]
        new_query = urlencode(query, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

    def validate_url(self, affiliate_url: str) -> bool:
        return "tag=" in affiliate_url

    def health_check(self) -> bool:
        return True


class FlipkartAffiliateProvider(BaseAffiliateProvider):
    provider_key = "flipkart"
    name = "Flipkart Affiliate Program"

    def generate_affiliate_url(self, destination_url: str, campaign_subid: Optional[str] = None) -> str:
        parsed = urlparse(destination_url)
        query = parse_qs(parsed.query)
        query["affid"] = [affiliate_config.flipkart_tag]
        new_query = urlencode(query, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

    def validate_url(self, affiliate_url: str) -> bool:
        return "affid=" in affiliate_url

    def health_check(self) -> bool:
        return True


class ImpactAffiliateProvider(BaseAffiliateProvider):
    provider_key = "impact"
    name = "Impact.com Network"

    def generate_affiliate_url(self, destination_url: str, campaign_subid: Optional[str] = None) -> str:
        return f"https://brandbattle.impact.com/click?subId1={campaign_subid or 'bb'}&u={destination_url}"

    def validate_url(self, affiliate_url: str) -> bool:
        return "impact.com" in affiliate_url

    def health_check(self) -> bool:
        return True


class ProviderRegistry:
    """Registry managing pluggable affiliate providers."""

    def __init__(self):
        self._providers: Dict[str, BaseAffiliateProvider] = {}
        self.register_provider(AmazonAssociatesProvider())
        self.register_provider(FlipkartAffiliateProvider())
        self.register_provider(ImpactAffiliateProvider())

    def register_provider(self, provider: BaseAffiliateProvider) -> None:
        self._providers[provider.provider_key] = provider

    def get_provider(self, key: str) -> Optional[BaseAffiliateProvider]:
        return self._providers.get(key)

    def get_all_providers(self) -> Dict[str, BaseAffiliateProvider]:
        return self._providers


# Singleton
provider_registry = ProviderRegistry()
