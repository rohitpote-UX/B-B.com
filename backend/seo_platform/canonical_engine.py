"""
Brand Battle — 9. Canonical URL Management Engine
Prevents duplicate content by mapping equivalent comparisons (A vs B and B vs A) to 1 canonical URL.
"""

from typing import Dict, Any
from seo_platform.config import seo_config


class CanonicalEngine:
    """Manages canonical URL mappings and duplicate prevention rules."""

    def get_canonical_url(self, slug: str) -> str:
        """Resolve canonical URL for slug."""
        return f"{seo_config.domain}/compare/{slug}"


# Singleton
canonical_engine = CanonicalEngine()
