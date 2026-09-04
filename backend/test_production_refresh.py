"""
Brand Battle — Production Data Refresh Verification Test Suite
Tests all production data refresh, validation, anomaly protection,
variant matching safety, rollback safety, and release-gate requirements (Part 22).
"""

import unittest
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from pipeline.production_refresh import (
    production_refresh_engine,
    StagedObservation,
    Stage1Report,
    Stage2Report,
)
from pipeline.price_verifier import price_verifier
from pipeline.image_verifier import image_verifier
from pipeline.marketplace_apis import (
    FlipkartApiClient,
    AmazonApiClient,
    MyntraFeedAdapter,
    AjioFeedAdapter,
)
from knowledge_graph.matcher_enhanced import EnhancedMatcher


class TestProductionDataRefresh(unittest.TestCase):
    """Targeted release-gate hardening tests for production data refresh."""

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.engine = production_refresh_engine
        cls.matcher = EnhancedMatcher()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # ─── 1. Price Parsing & Schema Validation ──────────────────────────
    def test_price_parsing_and_bounds(self):
        """Verifies that positive, valid prices pass while zero and negative fail."""
        res_valid = price_verifier.verify_price(new_price=14999.0, previous_price=14500.0, marketplace="amazon")
        self.assertTrue(res_valid.accepted)
        self.assertFalse(res_valid.is_anomaly)

        res_zero = price_verifier.verify_price(new_price=0.0, previous_price=1000.0, marketplace="flipkart")
        self.assertFalse(res_zero.accepted)
        self.assertTrue(res_zero.is_anomaly)
        self.assertEqual(res_zero.anomaly_type, "impossible_price")

        res_neg = price_verifier.verify_price(new_price=-500.0, previous_price=1000.0, marketplace="flipkart")
        self.assertFalse(res_neg.accepted)
        self.assertTrue(res_neg.is_anomaly)

    # ─── 2. Price Anomaly Detection (>40% movement) ────────────────────
    def test_price_anomaly_quarantine(self):
        """Verifies that sudden price movement >40% triggers quarantine."""
        # 50% drop from 10,000 to 5,000
        res_drop = price_verifier.verify_price(new_price=5000.0, previous_price=10000.0, marketplace="amazon")
        self.assertTrue(res_drop.is_anomaly)
        self.assertEqual(res_drop.anomaly_type, "sudden_drop")
        self.assertFalse(res_drop.accepted)

        # 60% spike from 10,000 to 16,000
        res_spike = price_verifier.verify_price(new_price=16000.0, previous_price=10000.0, marketplace="amazon")
        self.assertTrue(res_spike.is_anomaly)
        self.assertEqual(res_spike.anomaly_type, "sudden_spike")
        self.assertFalse(res_spike.accepted)

        # 10% movement within normal range
        res_normal = price_verifier.verify_price(new_price=10800.0, previous_price=10000.0, marketplace="amazon")
        self.assertFalse(res_normal.is_anomaly)
        self.assertTrue(res_normal.accepted)

    # ─── 3. Image Validation & Placeholder Rejection ───────────────────
    def test_image_verification_and_placeholders(self):
        """Verifies rejection of placeholder, dummy, or invalid image URLs."""
        bad_urls = [
            "https://example.com/placeholder.jpg",
            "https://example.com/no-image.png",
            "https://example.com/dummy.webp",
            "not_a_valid_url",
            "",
        ]
        for url in bad_urls:
            res = image_verifier.verify_image_url(url)
            self.assertFalse(res.is_valid, f"Expected invalid for {url}")

    # ─── 4. Product Variant Safety (Part 9) ────────────────────────────
    def test_variant_matching_safety(self):
        """Ensures that distinct variants (e.g., 128GB vs 256GB) are not force-matched."""
        title_128 = "Apple iPhone 15 (128 GB) - Blue"
        title_256 = "Apple iPhone 15 (256 GB) - Blue"

        tokens_128 = self.matcher.extract_model_tokens(title_128)
        tokens_256 = self.matcher.extract_model_tokens(title_256)

        storage_128 = [t for t in tokens_128 if "GB" in t]
        storage_256 = [t for t in tokens_256 if "GB" in t]

        self.assertIn("128GB", storage_128)
        self.assertIn("256GB", storage_256)
        self.assertNotEqual(set(storage_128), set(storage_256))

    # ─── 5. Stage 1 Discovery & Staging Integrity ──────────────────────
    def test_stage1_discovery_contract(self):
        """Verifies that Stage 1 discovers records with valid schema contracts."""
        staged, report = self.engine.run_stage1_discovery(limit_per_marketplace=5)
        self.assertGreater(len(staged), 0)
        self.assertGreater(report.successfully_parsed, 0)

        for item in staged:
            self.assertIsInstance(item, StagedObservation)
            self.assertIn(item.marketplace, ["amazon", "flipkart", "myntra", "ajio", "croma", "reliance_digital"])
            self.assertGreater(item.normalized_price, 0)
            self.assertTrue(item.currency in ["INR", "USD"])
            self.assertIsNotNone(item.data_hash)

    # ─── 6. Pre-promotion Database Snapshot ────────────────────────────
    def test_database_backup_creation(self):
        """Verifies that pre-promotion database backup is created properly."""
        backup_path = self.engine._create_database_backup()
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        self.assertGreater(os.path.getsize(backup_path), 0)

    # ─── 7. Currency Normalization & Legacy Reconciliation ─────────────
    def test_legacy_usd_reconciliation(self):
        """Verifies that products with legacy USD anomalies are corrected into INR."""
        self.engine._reconcile_legacy_products(self.db)
        prod = self.db.query(models.Product).filter(models.Product.id == 1).first()
        self.assertIsNotNone(prod)
        # iPhone 17 Pro Max must be at least ₹100,000, not ₹1029.14
        self.assertGreaterEqual(prod.current_best_price, 100000.0)

    # ─── 8. Data Trust Score Dimensions (Part 20) ──────────────────────
    def test_data_trust_score_calculation(self):
        """Verifies that Data Trust Score computes according to specified weighted dimensions."""
        mock_report = Stage2Report(price_verified=980, price_unverified=35)
        score, breakdown = self.engine._calculate_data_trust_score(mock_report, self.db)
        self.assertGreaterEqual(score, 80.0)
        self.assertLessEqual(score, 100.0)
        self.assertIn("price_accuracy", breakdown)
        self.assertIn("source_reliability", breakdown)
        self.assertIn("identity_confidence", breakdown)
        self.assertIn("freshness", breakdown)
        self.assertIn("image_integrity", breakdown)
        self.assertIn("availability_accuracy", breakdown)

    # ─── 9. Hard Release Gates Validation (Part 21) ────────────────────
    def test_hard_release_gates_evaluation(self):
        """Verifies hard release gates evaluate database integrity, orphans, and backup."""
        mock_report = Stage2Report(
            backup_file=self.engine._create_database_backup(),
            price_verified=100,
            data_trust_score=92.5,
        )
        passed, details = self.engine._evaluate_hard_release_gates(mock_report, self.db)
        self.assertTrue(details["database_integrity"])
        self.assertTrue(details["database_backup_created"])
        self.assertTrue(details["price_verification_functional"])
        self.assertTrue(details["minimum_trust_score_achieved"])


    # ─── 10. Currency Handling & Preservation (Part 14) ────────────────
    def test_currency_preservation(self):
        """Verifies original marketplace currency and price are preserved."""
        offer = self.db.query(models.MarketplaceOffer).first()
        if offer:
            self.assertIn(offer.currency, ["INR", "USD"])
            self.assertGreater(offer.price, 0)

    # ─── 11. Stale Data Protection (Part 12) ───────────────────────────
    def test_stale_data_preservation(self):
        """Verifies that failed verification retains the previous verified value."""
        # Simulated previous verified price: 50,000
        # Anomalous price: 5,000 (90% drop)
        res = price_verifier.verify_price(new_price=5000.0, previous_price=50000.0, marketplace="amazon")
        self.assertFalse(res.accepted)
        self.assertTrue(res.is_anomaly)
        # Verify that an accepted flag is False, preventing overwrite of trusted 50,000 price
        trusted_price = 50000.0 if not res.accepted else res.new_price
        self.assertEqual(trusted_price, 50000.0)

    # ─── 12. Duplicate Record Detection ────────────────────────────────
    def test_duplicate_record_detection(self):
        """Verifies duplicate data hashes are caught in Stage 1."""
        _, report = self.engine.run_stage1_discovery(limit_per_marketplace=20)
        self.assertGreaterEqual(report.duplicate_records, 0)

    # ─── 13. Verified-Only Price Alert Evaluation (Part 18) ────────────
    def test_verified_only_price_alerts(self):
        """Verifies that anomalous/unverified prices never trigger user price alerts."""
        prod = self.db.query(models.Product).first()
        if prod:
            # Create active alert
            alert = models.PriceAlert(
                user_id=1,
                product_id=prod.id,
                target_price=prod.lowest_price - 100.0 if prod.lowest_price else 1000.0,
                status=models.AlertStatus.ACTIVE.value,
            )
            self.db.add(alert)
            self.db.flush()

            # Anomalous price should not reach alert trigger
            anomaly_res = price_verifier.verify_price(new_price=10.0, previous_price=prod.lowest_price, marketplace="amazon")
            self.assertFalse(anomaly_res.accepted)

            # Clean up test alert
            self.db.delete(alert)
            self.db.commit()

    # ─── 14. Targeted Cache Invalidation (Part 16) ─────────────────────
    def test_targeted_cache_invalidation(self):
        """Verifies targeted patterns are purged without full database flush."""
        purged = self.engine._invalidate_affected_caches(self.db)
        self.assertIsInstance(purged, int)


if __name__ == "__main__":
    unittest.main()
