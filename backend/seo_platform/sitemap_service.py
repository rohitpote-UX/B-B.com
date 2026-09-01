"""
Brand Battle — 8. Dynamic Sitemap Generation Service
Generates XML sitemaps for comparison, product, category, and brand landing pages.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
from seo_platform.config import seo_config


class DynamicSitemapService:
    """Generates XML sitemap indexes and URL sets for search crawlers."""

    def generate_sitemap_xml(self, urls: List[str]) -> str:
        """Generate XML sitemap string."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for url in urls:
            xml_lines.append(f'  <url>')
            xml_lines.append(f'    <loc>{url}</loc>')
            xml_lines.append(f'    <lastmod>{now_iso}</lastmod>')
            xml_lines.append(f'    <changefreq>daily</changefreq>')
            xml_lines.append(f'    <priority>0.8</priority>')
            xml_lines.append(f'  </url>')
        xml_lines.append('</urlset>')
        return "\n".join(xml_lines)


# Singleton
dynamic_sitemap_service = DynamicSitemapService()
