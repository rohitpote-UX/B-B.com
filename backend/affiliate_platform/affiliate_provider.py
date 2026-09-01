"""
Brand Battle — 1. Affiliate Provider Abstraction Interface
Abstract Base Class defining standard adapter interface for all global affiliate networks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAffiliateProvider(ABC):
    """Abstract Base Class for pluggable affiliate network providers."""

    @property
    @abstractmethod
    def provider_key(self) -> str:
        """Unique provider identifier (e.g., 'amazon', 'flipkart', 'impact')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass

    @abstractmethod
    def generate_affiliate_url(self, destination_url: str, campaign_subid: Optional[str] = None) -> str:
        """Generate affiliate tracking URL for destination product link."""
        pass

    @abstractmethod
    def validate_url(self, affiliate_url: str) -> bool:
        """Validate affiliate URL syntax and tracking parameters."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Perform provider API or network health check."""
        pass
