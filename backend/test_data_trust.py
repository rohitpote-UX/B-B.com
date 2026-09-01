"""
Brand Battle — Production Data Trust Hardening Test Suite
Verifies data freshness engine, price anomaly detection, status calculation,
image URL validation, health logging, and DB schema integrity.
Uses standard library unittest for execution without external test framework dependencies.
"""

import unittest
from datetime import datetime, timezone, timedelta
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, engine, SessionLocal, init_db
from data_freshness import (
    determine_verification_status,
    get_freshness_display,
    get_product_ttl_tier,
    is_price_stale,
    PRICE_TTL_HOT,
    PRICE_TTL_STANDARD,
    PRICE_TTL_LOW_PRIORITY,
)
from pipeline.price_verifier import price_verifier
from pipeline.image_verifier import image_verifier
from pipeline.scrapers.base_scraper import (
    BaseScraper,
    RawProductItem,
    ScrapeResult,
    SCRAPE_STATUS_SUCCESS,
)
import models


class TestDataTrustHardening(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensures DB schema and migrations are initialized before tests."""
        init_db()

    # ─── 1. Data Freshness Engine Tests ──────────────────────────────

    def test_determine_verification_status_verified(self):
        """Timestamp within TTL returns 'verified'."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(seconds=100)
        self.assertEqual(determine_verification_status(recent, ttl_seconds=1800), "verified")

    def test_determine_verification_status_recently_verified(self):
        """Timestamp between 1x TTL and 2x TTL returns 'recently_verified'."""
        now = datetime.now(timezone.utc)
        within_2x = now - timedelta(seconds=2500)
        self.assertEqual(determine_verification_status(within_2x, ttl_seconds=1800), "recently_verified")

    def test_determine_verification_status_stale(self):
        """Timestamp beyond 2x TTL returns 'stale'."""
        now = datetime.now(timezone.utc)
        old = now - timedelta(seconds=5000)
        self.assertEqual(determine_verification_status(old, ttl_seconds=1800), "stale")

    def test_determine_verification_status_unverified(self):
        """None timestamp returns 'unverified'."""
        self.assertEqual(determine_verification_status(None, ttl_seconds=1800), "unverified")

    def test_get_freshness_display_labels(self):
        """Verifies human-readable freshness label formatting."""
        now = datetime.now(timezone.utc)
        self.assertEqual(get_freshness_display(None), "Not yet verified")
        self.assertEqual(get_freshness_display(now - timedelta(seconds=30)), "Verified just now")
        self.assertEqual(get_freshness_display(now - timedelta(minutes=5)), "Verified 5 min ago")
        self.assertEqual(get_freshness_display(now - timedelta(hours=3)), "Last checked 3 hours ago")
        self.assertEqual(get_freshness_display(now - timedelta(days=2)), "Last checked 2 days ago")

    def test_product_ttl_tier_assignment(self):
        """Verifies products are assigned correct TTL tiers based on views and alerts."""
        self.assertEqual(get_product_ttl_tier(view_count=10, alert_count=1), PRICE_TTL_HOT)
        self.assertEqual(get_product_ttl_tier(view_count=1500, alert_count=0), PRICE_TTL_HOT)
        self.assertEqual(get_product_ttl_tier(view_count=200, alert_count=0), PRICE_TTL_STANDARD)
        self.assertEqual(get_product_ttl_tier(view_count=10, alert_count=0), PRICE_TTL_LOW_PRIORITY)

    # ─── 2. Price Verification & Anomaly Detection Tests ─────────────────

    def test_price_verifier_normal_price(self):
        """Normal price check returns accepted verification result."""
        result = price_verifier.verify_price(
            new_price=100.0,
            previous_price=105.0,
            marketplace="amazon",
            source_method="api"
        )
        self.assertTrue(result.accepted)
        self.assertFalse(result.is_anomaly)
        self.assertEqual(result.verification_status, "verified")
        self.assertGreaterEqual(result.confidence_score, 0.8)

    def test_price_verifier_sudden_drop_anomaly(self):
        """Price drop >40% triggers anomaly flag and rejection for secondary verification."""
        result = price_verifier.verify_price(
            new_price=50.0,
            previous_price=100.0,
            marketplace="flipkart",
            source_method="scraper"
        )
        self.assertTrue(result.is_anomaly)
        self.assertEqual(result.anomaly_type, "sudden_drop")
        self.assertFalse(result.accepted)
        self.assertEqual(result.percentage_difference, 50.0)

    def test_price_verifier_impossible_price(self):
        """Zero or negative price is rejected immediately."""
        result = price_verifier.verify_price(
            new_price=0.0,
            previous_price=100.0,
            marketplace="amazon"
        )
        self.assertFalse(result.accepted)
        self.assertTrue(result.is_anomaly)
        self.assertEqual(result.anomaly_type, "impossible_price")

    def test_detect_price_anomaly_logging_dict(self):
        """Anomaly detector returns structured metadata dict for logging."""
        anomaly = price_verifier.detect_price_anomaly(
            product_id=1,
            new_price=20.0,
            previous_price=100.0,
            marketplace="croma"
        )
        self.assertIsNotNone(anomaly)
        self.assertEqual(anomaly["product_id"], 1)
        self.assertEqual(anomaly["anomaly_type"], "sudden_drop")
        self.assertEqual(anomaly["percentage_difference"], 80.0)

    # ─── 3. Image URL Verification Tests ─────────────────────────────────

    def test_image_verifier_empty_url(self):
        """Empty or invalid image URL fails verification gracefully."""
        res = image_verifier.verify_image_url("")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.verification_status, "failed_verification")

    def test_image_verifier_placeholder_url(self):
        """Placeholder image URLs are flagged as invalid."""
        res = image_verifier.verify_image_url("https://example.com/images/placeholder.png")
        self.assertFalse(res.is_valid)
        self.assertIn("placeholder", res.failure_reason.lower())

    def test_image_verifier_invalid_scheme(self):
        """Non-HTTP URLs are flagged as invalid."""
        res = image_verifier.verify_image_url("ftp://example.com/image.jpg")
        self.assertFalse(res.is_valid)
        self.assertIn("http", res.failure_reason.lower())

    # ─── 4. Scraper Base & Health Log Tests ──────────────────────────────

    def test_mock_scraper_stamps_parser_version_and_logs_health(self):
        """Scraper run_safe stamps parser version and logs health to DB."""
        class MockSuccessScraper(BaseScraper):
            PARSER_VERSION = "test_parser_v1"

            def __init__(self):
                super().__init__(marketplace="test_market", rate_limit_delay=0.01)

            def scrape(self, keyword: str):
                return [
                    RawProductItem(
                        raw_title="Test Item",
                        marketplace="test_market",
                        price=99.99,
                        product_url="https://test.com/item",
                        image_url="https://test.com/img.jpg"
                    )
                ]

        scraper = MockSuccessScraper()
        res = scraper.run_safe("test query")

        self.assertEqual(res.status, SCRAPE_STATUS_SUCCESS)
        self.assertEqual(res.products_found, 1)
        self.assertEqual(res.parser_version, "test_parser_v1")

        # Verify DB health log entry
        db = SessionLocal()
        try:
            log_entry = (
                db.query(models.ScraperHealthLog)
                .filter(models.ScraperHealthLog.marketplace == "test_market")
                .order_by(models.ScraperHealthLog.id.desc())
                .first()
            )
            self.assertIsNotNone(log_entry)
            self.assertEqual(log_entry.parser_version, "test_parser_v1")
            self.assertEqual(log_entry.products_found, 1)
            self.assertEqual(log_entry.status, SCRAPE_STATUS_SUCCESS)
        finally:
            db.close()

    # ─── 5. DB Verification Provenance Columns Test ──────────────────────

    def test_db_verification_provenance_columns(self):
        """Verifies that Price, Product, and MarketplaceOffer support verification fields."""
        db = SessionLocal()
        try:
            product = models.Product(
                name="Test Verification Phone",
                slug="test-verification-phone-unique",
                price_verification_status="verified",
                data_source="pipeline"
            )
            db.add(product)
            db.commit()
            db.refresh(product)

            self.assertIsNotNone(product.id)
            self.assertEqual(product.price_verification_status, "verified")
            self.assertEqual(product.data_source, "pipeline")

            price = models.Price(
                product_id=product.id,
                platform="amazon",
                price=49999.0,
                verification_status="verified",
                confidence_score=0.95,
                source_method="api"
            )
            db.add(price)
            db.commit()
            db.refresh(price)

            self.assertIsNotNone(price.id)
            self.assertEqual(price.verification_status, "verified")
            self.assertEqual(price.confidence_score, 0.95)

            db.delete(price)
            db.delete(product)
            db.commit()
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
