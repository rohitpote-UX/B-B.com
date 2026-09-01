"""
Brand Battle — 4. Link Validation Engine
Validates affiliate URL syntax, tracking parameters, and redirect health.
"""

from typing import Dict, Any
from affiliate_platform.provider_registry import provider_registry


class LinkValidationEngine:
    """Validates generated affiliate tracking links."""

    def validate_link(self, provider_key: str, affiliate_url: str) -> bool:
        provider = provider_registry.get_provider(provider_key)
        if provider:
            return provider.validate_url(affiliate_url)
        return True


# Singleton
link_validation_engine = LinkValidationEngine()
