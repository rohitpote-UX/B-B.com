"""
Brand Battle — Enterprise SEO System Master Verification Suite
Tests SEO Health Monitoring, Thin Content Evaluator, Dynamic Metadata Generators,
Schema.org JSON-LD Graph Validation, Sitemap Indexing, and Robots Directives.
"""

import sys
import os
import unittest

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db
from seo_platform.health_monitor import seo_health_monitor
from seo_platform.services import seo_platform_service
from seo_platform.sitemap_service import dynamic_sitemap_service
from seo_platform.robots_service import robots_service


class TestEnterpriseSeoSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes database connection and schema for SEO tests."""
        init_db()

    def test_seo_health_monitor_audit(self):
        """Verifies full database SEO health audit execution and score calculation."""
        db = SessionLocal()
        try:
            res = seo_health_monitor.run_full_seo_audit(db)
            self.assertIn("overall_seo_score", res)
            self.assertIn("metrics", res)
            self.assertIn("component_scores", res)
            self.assertGreaterEqual(res["overall_seo_score"], 0.0)
            self.assertLessEqual(res["overall_seo_score"], 100.0)
        finally:
            db.close()

    def test_evaluate_comparison_seo_payload(self):
        """Verifies comparison SEO evaluation produces valid metadata and JSON-LD schema."""
        db = SessionLocal()
        try:
            payload = seo_platform_service.evaluate_comparison_seo(db=db, p1_id=1, p2_id=2)
            self.assertTrue(payload.is_valid_seo)
            self.assertIn("Brand Battle", payload.title)
            self.assertIn("https://schema.org", payload.json_ld_schema.get("@context", ""))
        finally:
            db.close()

    def test_sitemap_xml_generation(self):
        """Verifies dynamic XML sitemap generation includes valid urlset tag."""
        urls = ["https://brandbattle.com/", "https://brandbattle.com/compare"]
        xml = dynamic_sitemap_service.generate_sitemap_xml(urls)
        self.assertIn("<urlset", xml)
        self.assertIn("<loc>https://brandbattle.com/</loc>", xml)

    def test_robots_txt_directives(self):
        """Verifies robots.txt generation contains required User-agent and Sitemap lines."""
        robots_txt = robots_service.generate_robots_txt()
        self.assertIn("User-agent:", robots_txt)
        self.assertIn("Sitemap:", robots_txt)
        self.assertIn("Disallow: /admin/", robots_txt)


if __name__ == "__main__":
    unittest.main()
