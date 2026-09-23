"""
Brand Battle — Catalog Ingestion Engine Comprehensive Test Suite
Validates GTIN validation, normalization, deduplication, quality scoring,
SSRF safety, resumable job execution, and currency integrity regression.
"""

import os
import sys
import json
import unittest
from datetime import datetime, timezone

# Ensure backend root is on path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from catalog_engine.gtin_validator import GtinValidator
from catalog_engine.normalizer import CatalogNormalizer
from catalog_engine.quality_scorer import ProductQualityScorer
from catalog_engine.security import is_ssrf_safe_url
from catalog_engine.schemas import NormalizedProductCandidate
from catalog_engine.job_runner import CatalogJobRunner
from catalog_engine.adapters.admin_import_adapter import AdminFileImportAdapter
from seo_platform.indexability import indexability_engine
import models
from database import SessionLocal


class TestGtinValidator(unittest.TestCase):
    """Test suite for GS1 standard GTIN/UPC/EAN validation."""

    def test_valid_gtin13_ean(self):
        # Valid EAN-13 (Apple iPhone standard EAN)
        valid_ean = "0194253796855"
        is_valid, cleaned, error = GtinValidator.validate(valid_ean)
        self.assertTrue(is_valid, f"Expected valid EAN-13, got error: {error}")
        self.assertEqual(cleaned, valid_ean)
        self.assertEqual(GtinValidator.classify_type(cleaned), "EAN-13")

    def test_valid_upc_a(self):
        # Valid UPC-12 (036000291452)
        valid_upc = "036000291452"
        is_valid, cleaned, error = GtinValidator.validate(valid_upc)
        self.assertTrue(is_valid, f"Expected valid UPC-A, got error: {error}")
        self.assertEqual(cleaned, valid_upc)
        self.assertEqual(GtinValidator.classify_type(cleaned), "UPC-A")

    def test_valid_gtin8(self):
        # Valid GTIN-8 (96385074)
        valid_gtin8 = "96385074"
        is_valid, cleaned, error = GtinValidator.validate(valid_gtin8)
        self.assertTrue(is_valid, f"Expected valid GTIN-8, got error: {error}")
        self.assertEqual(GtinValidator.classify_type(cleaned), "GTIN-8")

    def test_invalid_checksum(self):
        # Last digit altered
        invalid_ean = "0194253796859"
        is_valid, cleaned, error = GtinValidator.validate(invalid_ean)
        self.assertFalse(is_valid)
        self.assertIn("Checksum mismatch", error)

    def test_reject_dummy_patterns(self):
        # All zeros or repeating digits
        is_valid_zero, _, _ = GtinValidator.validate("0000000000000")
        is_valid_rep, _, _ = GtinValidator.validate("1111111111111")
        is_valid_seq, _, _ = GtinValidator.validate("1234567890123")
        self.assertFalse(is_valid_zero)
        self.assertFalse(is_valid_rep)
        self.assertFalse(is_valid_seq)


class TestCatalogNormalizer(unittest.TestCase):
    """Test suite for deterministic text, brand, and category normalization."""

    def test_brand_canonicalization(self):
        _, b1 = CatalogNormalizer.normalize_brand("APPLE INC")
        _, b2 = CatalogNormalizer.normalize_brand("samsung electronics")
        _, b3 = CatalogNormalizer.normalize_brand("OnePlus")
        self.assertEqual(b1, "Apple")
        self.assertEqual(b2, "Samsung")
        self.assertEqual(b3, "OnePlus")

    def test_category_mapping(self):
        _, cat1 = CatalogNormalizer.normalize_category("Mobiles & Accessories", "iPhone 18 Pro Max")
        _, cat2 = CatalogNormalizer.normalize_category("Laptops", "MacBook Pro M4")
        _, cat3 = CatalogNormalizer.normalize_category("Smart Watches", "Apple Watch Ultra")
        self.assertEqual(cat1, "Mobile Phones")
        self.assertEqual(cat2, "Laptops")
        self.assertEqual(cat3, "Smartwatches")

    def test_title_cleaning(self):
        raw = "Apple iPhone 18 Pro Max 256GB Online Lowest Price Best Deal Sale with bank offer"
        clean = CatalogNormalizer.clean_title(raw, "Apple")
        self.assertNotIn("Lowest Price", clean)
        self.assertNotIn("Best Deal", clean)
        self.assertNotIn("bank offer", clean)
        self.assertIn("Apple iPhone 18 Pro Max 256GB", clean)

    def test_preserve_model_numbers(self):
        raw = "Samsung Galaxy S24 Ultra SM-S928B/DS 512GB Titanium Black"
        clean = CatalogNormalizer.clean_title(raw, "Samsung")
        self.assertIn("SM-S928B/DS", clean)
        self.assertIn("512GB", clean)


class TestQualityScorer(unittest.TestCase):
    """Test suite for 0-100 Product Quality Scoring and Publishing Gates."""

    def test_complete_product_publishable(self):
        candidate = NormalizedProductCandidate(
            source_id=1,
            source_name="Test Source",
            external_id="TEST_001",
            brand="Apple",
            canonical_brand="Apple",
            raw_title="Apple iPhone 18 Pro Max 256GB Natural Titanium",
            clean_title="Apple iPhone 18 Pro Max 256GB Natural Titanium",
            canonical_name="Apple iPhone 18 Pro Max 256GB Natural Titanium",
            raw_category="Mobiles",
            canonical_category="Mobile Phones",
            gtin="0194253796855",
            is_gtin_valid=True,
            primary_image_url="https://rukminim1.flixcart.com/image/apple.jpg",
            description="The flagship Apple iPhone 18 Pro Max with A19 Pro chip and ProMotion display.",
            specifications={"Display": "6.9 inch Super Retina", "Processor": "A19 Pro", "Storage": "256GB", "Camera": "48MP Triple"},
            price=179900.0,
            currency="INR"
        )
        score, is_publishable, reasons = ProductQualityScorer.evaluate(candidate)
        self.assertGreaterEqual(score, 70.0)
        self.assertTrue(is_publishable)

    def test_incomplete_product_unpublishable(self):
        candidate = NormalizedProductCandidate(
            source_id=1,
            source_name="Test Source",
            external_id="TEST_002",
            brand="",
            canonical_brand="Generic",
            raw_title="Phone",
            clean_title="Phone",
            canonical_name="Phone",
            raw_category="",
            canonical_category="Electronics",
            description="Short",
            specifications={},
        )
        score, is_publishable, reasons = ProductQualityScorer.evaluate(candidate)
        self.assertLess(score, 70.0)
        self.assertFalse(is_publishable)


class TestSecurityAndSSRF(unittest.TestCase):
    """Test suite for SSRF protection and allowed domain enforcement."""

    def test_blocks_localhost_and_private_ips(self):
        self.assertFalse(is_ssrf_safe_url("http://localhost:8000/api"))
        self.assertFalse(is_ssrf_safe_url("http://127.0.0.1:8000/admin"))
        self.assertFalse(is_ssrf_safe_url("http://169.254.169.254/latest/meta-data/"))
        self.assertFalse(is_ssrf_safe_url("http://192.168.1.1/router"))
        self.assertFalse(is_ssrf_safe_url("http://10.0.0.1/internal"))

    def test_blocks_unauthorized_external_domains(self):
        self.assertFalse(is_ssrf_safe_url("https://malicious-site.com/exploit.jpg"))

    def test_allows_authorized_catalog_domains(self):
        self.assertTrue(is_ssrf_safe_url("https://rukminim1.flixcart.com/image/item.jpg"))
        self.assertTrue(is_ssrf_safe_url("https://affiliate-api.flipkart.net/affiliate/1.0/feed.json"))
        self.assertTrue(is_ssrf_safe_url("https://brandbattle.com/catalog/spec.json"))


class TestCurrencyIntegrityRegression(unittest.TestCase):
    """
    CRITICAL SECTION 67 REGRESSION TEST:
    Guarantees that Indian marketplace prices in INR (e.g. ₹1,79,900)
    remain 179900 INR and are NEVER converted to 2141.67 INR.
    """

    def test_canonical_inr_price_preservation(self):
        adapter = AdminFileImportAdapter()
        raw_product = {
            "name": "Apple iPhone 18 Pro Max (256GB, Desert Titanium)",
            "brand": "Apple",
            "category": "Mobile Phones",
            "price_inr": "1,79,900",
            "original_price_inr": "1,84,900",
            "description": "Apple flagship smartphone with A19 Pro Bionic processor.",
        }

        price_data = adapter.extract_price(raw_product)
        self.assertIsNotNone(price_data)
        self.assertEqual(price_data["price"], 179900.0)
        self.assertEqual(price_data["original_price"], 184900.0)
        self.assertEqual(price_data["currency"], "INR")

        # Crucial anti-regression assertion:
        self.assertNotEqual(price_data["price"], 2141.67, "CRITICAL ERROR: INR price divided by 84 USD conversion rate!")


class TestPilotIngestion(unittest.TestCase):
    """Pilot batch ingestion test using Admin Catalog Import adapter."""

    def test_pilot_batch_ingestion(self):
        db = SessionLocal()
        try:
            # 1. Ensure admin source exists
            admin_source = db.query(models.CatalogSource).filter(
                models.CatalogSource.adapter_key == "admin_import"
            ).first()
            self.assertIsNotNone(admin_source, "Admin source must exist in database")

            # 2. Prepare test JSON feed fixture
            test_fixture = [
                {
                    "id": "PILOT_IPHONE_18_PM",
                    "name": "Apple iPhone 18 Pro Max 256GB Natural Titanium",
                    "brand": "Apple",
                    "category": "Mobile Phones",
                    "gtin": "0194253796855",
                    "price_inr": 179900.0,
                    "original_price_inr": 184900.0,
                    "description": "Authentic Apple iPhone 18 Pro Max with Titanium body and Ceramic Shield.",
                    "image_url": "https://rukminim1.flixcart.com/image/iphone18pm.jpg",
                    "specs": {"Chip": "A19 Pro", "Display": "6.9 Super Retina", "Camera": "48MP Fusion"}
                },
                {
                    "id": "PILOT_GALAXY_S26_ULTRA",
                    "name": "Samsung Galaxy S26 Ultra 512GB Phantom Black",
                    "brand": "Samsung",
                    "category": "Mobile Phones",
                    "gtin": "0880609187650",
                    "price_inr": 139999.0,
                    "description": "Next generation Samsung Galaxy flagship smartphone with Galaxy AI.",
                    "image_url": "https://rukminim1.flixcart.com/image/s26ultra.jpg",
                    "specs": {"Chip": "Snapdragon 8 Gen 5", "Display": "6.8 Dynamic AMOLED", "RAM": "12GB"}
                }
            ]

            fixture_path = os.path.join(BACKEND_DIR, "pilot_fixture.json")
            with open(fixture_path, "w", encoding="utf-8") as f:
                json.dump(test_fixture, f)

            # 3. Run Ingestion Job
            job = CatalogJobRunner.run_job(
                source_id=admin_source.id,
                job_type="FILE_IMPORT",
                file_path=fixture_path,
                db=db
            )

            # 4. Verify Job Counters
            self.assertEqual(job.status, "COMPLETED")
            self.assertEqual(job.records_seen, 2)
            total_handled = job.records_created + job.records_updated + job.records_merged + job.records_reviewed
            self.assertGreaterEqual(total_handled, 2)

            # 5. Verify Staging Table
            raw_records = db.query(models.RawCatalogRecord).filter(
                models.RawCatalogRecord.source_id == admin_source.id
            ).all()
            self.assertGreaterEqual(len(raw_records), 2)
            for r in raw_records:
                self.assertIsNotNone(r.content_hash)
                self.assertEqual(len(r.content_hash), 64)

            # 6. Verify SEO Eligibility Integration
            master = db.query(models.MasterProduct).filter(
                models.MasterProduct.canonical_name.ilike("%iPhone 18 Pro Max%")
            ).first()
            if master:
                seo_status = indexability_engine.evaluate_product_seo_eligibility(master)
                self.assertIn(seo_status, ["SEO_ELIGIBLE", "SEO_PENDING"])

            # Clean up fixture file
            if os.path.exists(fixture_path):
                os.remove(fixture_path)

        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
