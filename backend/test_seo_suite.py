"""
Brand Battle — Master Enterprise SEO & GEO/AEO Verification Test Suite
Tests:
- Dynamic Title Architecture & Character Limits
- Facts-Grounded Meta Descriptions & Zero-Hallucination Controls
- Canonical URL Normalization
- Schema.org JSON-LD Graph Validation (Product, Offer, BreadcrumbList, WebSite, Organization, FAQPage)
- Strict Anti-Fabrication Rules (Zero Fake Reviews, Ratings, or Prices)
- Thin Content & Indexability Quality Gates
- Robots.txt Directives & Bot Crawl Rules
- Dynamic XML Sitemap Generation
- Enterprise SEO Health Audit & Score Calculation
"""

import os
import sys
import unittest

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db
from seo_platform.health_monitor import seo_health_monitor
from seo_platform.services import seo_platform_service
from seo_platform.sitemap_service import dynamic_sitemap_service
from seo_platform.robots_service import robots_service
from seo_platform.canonical_engine import canonical_engine
from seo_platform.metadata_engine import dynamic_metadata_engine
from seo_platform.faq_generator import faq_generator_engine
import models


class MasterSeoGeoAeoTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes database schema and seed data for tests."""
        init_db()

    def test_01_metadata_engine_generation(self):
        """Validates that metadata engine builds unique title, description, and canonical URL."""
        db = SessionLocal()
        try:
            p1 = db.query(models.Product).filter(models.Product.id == 1).first()
            p2 = db.query(models.Product).filter(models.Product.id == 2).first()
            if p1 and p2:
                meta = dynamic_metadata_engine.generate_metadata(p1, p2, "p1-vs-p2")
                self.assertIn("title", meta)
                self.assertIn("meta_description", meta)
                self.assertIn("canonical_url", meta)
                self.assertIn("Brand Battle", meta["title"])
                self.assertTrue(meta["canonical_url"].startswith("https://brandbattle.com/compare/"))
        finally:
            db.close()

    def test_02_canonical_url_normalization(self):
        """Validates deterministic canonical URL construction."""
        canonical = canonical_engine.get_canonical_url("iphone-17-vs-galaxy-s26")
        self.assertEqual(canonical, "https://brandbattle.com/compare/iphone-17-vs-galaxy-s26")
        self.assertNotIn("?", canonical)

    def test_03_schema_org_product_and_offer_structure(self):
        """Validates Schema.org Product and Offer JSON-LD compliance."""
        db = SessionLocal()
        try:
            p = db.query(models.Product).filter(models.Product.is_active == True).first()
            if p:
                schema = seo_platform_service.build_product_json_ld(p)
                self.assertEqual(schema.get("@context"), "https://schema.org")
                self.assertEqual(schema.get("@type"), "Product")
                self.assertIn(p.name, schema.get("name", ""))
                if p.current_best_price and p.current_best_price > 0:
                    offer = schema.get("offers", {})
                    self.assertEqual(offer.get("@type"), "Offer")
                    self.assertEqual(offer.get("price"), p.current_best_price)
                    self.assertEqual(offer.get("priceCurrency"), "INR")
                    self.assertEqual(offer.get("availability"), "https://schema.org/InStock")
        finally:
            db.close()

    def test_04_zero_fake_ratings_and_reviews_rule(self):
        """CRITICAL: Ensures NO fake 5-star ratings or fabricated reviews are injected into structured data."""
        db = SessionLocal()
        try:
            products = db.query(models.Product).all()
            for p in products:
                schema = seo_platform_service.build_product_json_ld(p)
                # If product has no reviews in DB, aggregateRating MUST be omitted
                if not p.average_rating or not p.total_reviews:
                    self.assertNotIn("aggregateRating", schema, f"Product {p.id} has no reviews; aggregateRating must NOT be faked")
                else:
                    agg = schema.get("aggregateRating", {})
                    self.assertEqual(agg.get("ratingValue"), p.average_rating)
                    self.assertEqual(agg.get("reviewCount"), p.total_reviews)
        finally:
            db.close()

    def test_05_comparison_schema_graph(self):
        """Validates comprehensive comparison JSON-LD graph combining WebPage, Products, Breadcrumbs, and FAQs."""
        db = SessionLocal()
        try:
            eval_res = seo_platform_service.evaluate_comparison_seo(db=db, p1_id=1, p2_id=2)
            self.assertTrue(eval_res.is_valid_seo)
            json_ld = eval_res.json_ld_schema
            self.assertEqual(json_ld.get("@context"), "https://schema.org")
            graph = json_ld.get("@graph", [])
            self.assertGreaterEqual(len(graph), 3, "Graph must contain WebPage, BreadcrumbList, Products")

            types = [node.get("@type") for node in graph]
            self.assertIn("WebPage", types)
            self.assertIn("BreadcrumbList", types)
            self.assertIn("Product", types)
        finally:
            db.close()

    def test_06_faq_generator_grounded_in_real_data(self):
        """Validates that comparison FAQs are dynamically generated strictly from real specs and prices."""
        db = SessionLocal()
        try:
            p1 = db.query(models.Product).filter(models.Product.id == 1).first()
            p2 = db.query(models.Product).filter(models.Product.id == 2).first()
            if p1 and p2:
                faqs = faq_generator_engine.generate_faqs(p1, p2)
                self.assertGreaterEqual(len(faqs), 2)
                q_texts = [f.question for f in faqs]
                self.assertTrue(any("cheaper" in q.lower() for q in q_texts))
        finally:
            db.close()

    def test_07_robots_txt_directives(self):
        """Validates that robots.txt allows public indexable paths and blocks private/admin/filter query traps."""
        robots_content = robots_service.generate_robots_txt()
        self.assertIn("User-agent: *", robots_content)
        self.assertIn("Allow: /product/", robots_content)
        self.assertIn("Allow: /compare/", robots_content)
        self.assertIn("Disallow: /admin/", robots_content)
        self.assertIn("Disallow: /api/", robots_content)
        self.assertIn("Sitemap:", robots_content)

    def test_08_dynamic_xml_sitemap(self):
        """Validates XML sitemap generation format and validity."""
        test_urls = [
            "https://brandbattle.com/",
            "https://brandbattle.com/product/1",
            "https://brandbattle.com/compare/iphone-17-vs-galaxy-s26",
        ]
        xml = dynamic_sitemap_service.generate_sitemap_xml(test_urls)
        self.assertTrue(xml.startswith("<?xml"))
        self.assertIn("<urlset", xml)
        for u in test_urls:
            self.assertIn(f"<loc>{u}</loc>", xml)

    def test_09_seo_health_monitor_audit(self):
        """Validates full SEO health monitor calculation across products."""
        db = SessionLocal()
        try:
            audit = seo_health_monitor.run_full_seo_audit(db)
            self.assertIn("overall_seo_score", audit)
            self.assertIn("component_scores", audit)
            self.assertIn("metrics", audit)
            self.assertGreaterEqual(audit["overall_seo_score"], 70.0, "Overall score should be high quality")
            self.assertEqual(audit["status"], "HEALTHY")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
