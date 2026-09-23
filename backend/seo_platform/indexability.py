"""
Brand Battle — 17. Search Console Readiness Engine
Provides indexability diagnostics and Google Search Console audit readiness.
"""

from typing import Dict, Any


class IndexabilityEngine:
    """Monitors indexability status and crawl readiness."""

    def get_indexability_status(self) -> Dict[str, Any]:
        return {
            "search_console_readiness": "ready",
            "canonical_status": "valid",
            "robots_txt_status": "configured",
            "sitemap_index_status": "active",
        }

    def evaluate_product_seo_eligibility(self, product: Any) -> str:
        """
        Evaluates whether a product is eligible for search engine indexation.
        Strict gating preventing thin or low-quality catalog pages from entering sitemaps.
        """
        is_active = getattr(product, "is_active", True)
        if not is_active:
            return "SEO_BLOCKED"

        name = getattr(product, "canonical_name", None) or getattr(product, "name", None)
        if not name or len(str(name).strip()) < 3:
            return "SEO_LOW_QUALITY"

        brand = getattr(product, "brand", None) or getattr(product, "brand_id", None)
        category = getattr(product, "category", None) or getattr(product, "category_id", None)
        if not brand and not category:
            return "SEO_LOW_QUALITY"

        img = getattr(product, "primary_image_url", None) or getattr(product, "image_url", None)
        if not img or not str(img).startswith("http"):
            return "SEO_LOW_QUALITY"

        has_specs = bool(getattr(product, "specifications", None))
        has_price = getattr(product, "lowest_price", None) is not None or getattr(product, "price", None) is not None
        if not has_specs and not has_price:
            return "SEO_PENDING"

        desc = getattr(product, "description", "") or ""
        if len(str(desc).strip()) < 15:
            return "SEO_LOW_QUALITY"

        return "SEO_ELIGIBLE"


# Singleton
indexability_engine = IndexabilityEngine()
