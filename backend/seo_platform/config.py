"""
Brand Battle — Enterprise SEO Comparison Publishing Platform Configuration
SEO thresholds, metadata rules, canonical domain, and performance targets (<20ms metadata generation).
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class SeoSLOs(BaseModel):
    """Performance targets (milliseconds)."""
    metadata_generation_ms: int = 20
    structured_data_generation_ms: int = 20
    page_render_cached_ms: int = 150


class SeoPlatformConfig(BaseModel):
    """Master configuration for the SEO Platform."""
    enabled: bool = True
    version: str = "v10.0-enterprise-seo-publishing-platform"
    domain: str = "https://brandbattle.com"
    site_name: str = "Brand Battle"
    slo: SeoSLOs = SeoSLOs()

    # Feature flags
    enable_ai_content: bool = True
    enable_schema_jsonld: bool = True
    enable_dynamic_sitemaps: bool = True
    enable_seo_validator: bool = True


seo_config = SeoPlatformConfig()
