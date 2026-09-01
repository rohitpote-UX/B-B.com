"""
Brand Battle — 1. Dynamic SEO Metadata Engine & 15. OpenGraph Engine
Generates unique title tags, meta descriptions, canonical URLs, robots directives, OpenGraph, and Twitter Cards (<20ms latency target).
"""

from typing import Dict, Any
from models import Product
from seo_platform.config import seo_config
from seo_platform.schemas import OpenGraphSchema


class DynamicMetadataEngine:
    """Generates unique SEO metadata for every comparison landing page."""

    def generate_metadata(self, p1: Product, p2: Product, canonical_slug: str) -> Dict[str, Any]:
        """Generate title, description, OpenGraph, and canonical URL targeting <20ms latency."""
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()

        price1 = getattr(p1, "current_best_price", 0.0) or 0.0
        price2 = getattr(p2, "current_best_price", 0.0) or 0.0

        title = f"{name1} vs {name2} | AI Comparison, Specs & Best Choice | Brand Battle"
        meta_desc = (
            f"Compare {name1} (₹{price1:,.0f}) and {name2} (₹{price2:,.0f}) side-by-side. "
            f"Discover verified specs, 5-year ownership costs, AI recommendations, and live marketplace deals on Brand Battle."
        )
        canonical_url = f"{seo_config.domain}/compare/{canonical_slug}"
        image_url = getattr(p1, "image_url", None) or f"{seo_config.domain}/og-compare.png"

        og = OpenGraphSchema(
            title=title,
            description=meta_desc,
            url=canonical_url,
            image_url=image_url,
        )

        return {
            "title": title,
            "meta_description": meta_desc,
            "canonical_url": canonical_url,
            "open_graph": og.model_dump(),
            "robots_directive": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        }


# Singleton
dynamic_metadata_engine = DynamicMetadataEngine()
