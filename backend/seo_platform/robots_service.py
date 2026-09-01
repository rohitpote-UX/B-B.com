"""
Brand Battle — 16. Robots & Crawl Management Service
Generates robots.txt directives and crawl optimization rules.
"""

from seo_platform.config import seo_config


class RobotsService:
    """Generates robots.txt directives."""

    def generate_robots_txt(self) -> str:
        return (
            f"User-agent: *\n"
            f"Allow: /\n"
            f"Allow: /product/\n"
            f"Allow: /compare/\n"
            f"Disallow: /admin/\n"
            f"Disallow: /api/\n\n"
            f"Sitemap: {seo_config.domain}/api/seo/sitemap.xml\n"
        )


# Singleton
robots_service = RobotsService()
