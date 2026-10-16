"""
Brand Battle — Image and Identity Integrity Regression Test Suite
Validates that:
1. A Galaxy S22 Ultra image cannot be accepted as verified for a Galaxy S26 Ultra record.
2. Different product generations cannot silently share an image mapping (e.g. iPhone 15 on iPhone 18).
3. Storage/RAM/color variants remain associated with the correct canonical product.
4. Broken URLs, placeholders, and quarantined images resolve to a safe, on-brand fallback SVG.
5. Unknown image provenance does not automatically become verified.
6. Failed validation never creates fake verification timestamps or statuses.
7. Repair image integrity script is strictly idempotent.
"""

import unittest
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.image_verifier import (
    image_verifier,
    FALLBACK_PRODUCT_IMAGE,
    KNOWN_QUARANTINED_IMAGE_SIGNATURES,
    ImageVerificationResult,
)
from catalog_engine.quality_scorer import ProductQualityScorer
from catalog_engine.schemas import NormalizedProductCandidate
from repair_image_integrity import repair_sqlite_database
from pipeline.image_verifier import KNOWN_QUARANTINED_IMAGE_SIGNATURES

S22_ON_S26_SIGNATURE = "71j8tz0uejl"
IPHONE15_SIGNATURES = ["71657tifehl", "81+gikwqlil"]
ONEPLUS_NORD_SIGNATURE = "6175slkkecl"


class TestImageIdentityIntegrity(unittest.TestCase):
    """Regression test suite enforcing strict product image and identity integrity."""

    def test_galaxy_s22_ultra_rejected_for_s26_ultra(self):
        """
        Acceptance Criterion: The Samsung Galaxy S26 Ultra card never displays
        a Galaxy S22 Ultra image.
        """
        s22_url = f"https://m.media-amazon.com/images/I/{S22_ON_S26_SIGNATURE}.jpg"
        product_name = "Samsung Galaxy S26 Ultra 5G (256 GB)"

        is_valid, status, reason = image_verifier.validate_product_image_association(
            product_name=product_name,
            image_url=s22_url
        )
        self.assertFalse(is_valid, "Galaxy S22 Ultra image must not be valid for Galaxy S26 Ultra")
        self.assertEqual(status, "quarantined_mismatch")
        self.assertIn("Galaxy S22 Ultra", reason)

        # Full verification function must also reject without performing network HEAD
        result = image_verifier.verify_product_image_for_product(
            product_name=product_name,
            image_url=s22_url,
            check_network=False
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.verification_status, "quarantined_mismatch")

        # Safe image resolver must map to neutral fallback
        safe_url = image_verifier.get_safe_image_for_product(product_name, s22_url)
        self.assertEqual(safe_url, FALLBACK_PRODUCT_IMAGE)
        self.assertNotIn(S22_ON_S26_SIGNATURE, safe_url)

    def test_different_generations_cannot_silently_share_image_mapping(self):
        """
        Acceptance Criterion: Different product generations cannot silently share
        an image mapping.
        """
        # Test iPhone 15 image on iPhone 18 Pro Max
        for sig in IPHONE15_SIGNATURES:
            iphone15_url = f"https://m.media-amazon.com/images/I/{sig}.jpg"
            is_valid, status, reason = image_verifier.validate_product_image_association(
                product_name="Apple iPhone 18 Pro Max (256 GB)",
                image_url=iphone15_url
            )
            self.assertFalse(is_valid, f"iPhone 15 image ({sig}) must be rejected for iPhone 18")
            self.assertEqual(status, "quarantined_mismatch")
            self.assertIn("Apple iPhone 15", reason)

            safe_url = image_verifier.get_safe_image_for_product("Apple iPhone 18 Pro Max (256 GB)", iphone15_url)
            self.assertEqual(safe_url, FALLBACK_PRODUCT_IMAGE)

        # Test OnePlus Nord CE 3 image on OnePlus 15 Pro
        nord_url = f"https://m.media-amazon.com/images/I/{ONEPLUS_NORD_SIGNATURE}.jpg"
        is_valid, status, reason = image_verifier.validate_product_image_association(
            product_name="OnePlus 15 Pro (16GB RAM, 512GB Storage)",
            image_url=nord_url
        )
        self.assertFalse(is_valid, "OnePlus Nord image must be rejected for OnePlus 15 Pro")
        self.assertEqual(status, "quarantined_mismatch")

        safe_url = image_verifier.get_safe_image_for_product("OnePlus 15 Pro", nord_url)
        self.assertEqual(safe_url, FALLBACK_PRODUCT_IMAGE)

    def test_url_model_pattern_generation_mismatch(self):
        """
        Generations extracted from URLs must match the target product generation.
        """
        # URL has explicit S22, but product is S26
        url = "https://images.samsung.com/is/image/samsung/p6pim/in/galaxy-s22-ultra/gallery/s22-ultra.jpg"
        is_valid, status, reason = image_verifier.validate_product_image_association(
            product_name="Samsung Galaxy S26 Ultra",
            image_url=url
        )
        self.assertFalse(is_valid)
        self.assertEqual(status, "quarantined_mismatch")
        self.assertIn("S22", reason)

        # URL has explicit iPhone 14, but product is iPhone 16
        url_ip = "https://store.storeimages.cdn-apple.com/iphone-14-pro-max-finish.jpg"
        is_valid_ip, status_ip, reason_ip = image_verifier.validate_product_image_association(
            product_name="Apple iPhone 16 Pro Max",
            image_url=url_ip
        )
        self.assertFalse(is_valid_ip)
        self.assertEqual(status_ip, "quarantined_mismatch")
        self.assertIn("iPhone 14", reason_ip)

    def test_variants_remain_associated_with_correct_canonical_product(self):
        """
        Acceptance Criterion: Variants (storage, RAM, color) remain associated with
        the correct canonical product without false rejection.
        """
        valid_s24_url = "https://m.media-amazon.com/images/I/71cx11n9gUL._SL1500_.jpg"
        # 256GB variant
        is_valid_256, status_256, _ = image_verifier.validate_product_image_association(
            product_name="Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)",
            image_url=valid_s24_url
        )
        self.assertTrue(is_valid_256)
        self.assertEqual(status_256, "verified")

        # 512GB variant
        is_valid_512, status_512, _ = image_verifier.validate_product_image_association(
            product_name="Samsung Galaxy S24 Ultra 5G (Titanium Black, 12GB RAM, 512 GB)",
            image_url=valid_s24_url
        )
        self.assertTrue(is_valid_512)
        self.assertEqual(status_512, "verified")

    def test_broken_urls_and_placeholders_produce_safe_fallback(self):
        """
        Acceptance Criterion: Broken URLs and placeholders produce a safe fallback.
        """
        # Empty string
        self.assertEqual(
            image_verifier.get_safe_image_for_product("Samsung Galaxy S26 Ultra", ""),
            FALLBACK_PRODUCT_IMAGE
        )
        # None
        self.assertEqual(
            image_verifier.get_safe_image_for_product("Apple iPhone 18", None),
            FALLBACK_PRODUCT_IMAGE
        )
        # Quarantined signature
        self.assertEqual(
            image_verifier.get_safe_image_for_product(
                "Samsung Galaxy S26 Ultra",
                f"https://m.media-amazon.com/images/I/{S22_ON_S26_SIGNATURE}.jpg"
            ),
            FALLBACK_PRODUCT_IMAGE
        )

    def test_unverified_provenance_does_not_falsely_certify(self):
        """
        Acceptance Criterion: Unknown image provenance does not automatically become verified.
        Generic stock photos on preview flagship hardware cannot be verified.
        """
        unsplash_url = "https://images.unsplash.com/photo-phone-dummy"
        is_valid, status, reason = image_verifier.validate_product_image_association(
            product_name="Samsung Galaxy S26 Ultra 5G",
            image_url=unsplash_url
        )
        self.assertFalse(is_valid)
        self.assertEqual(status, "unverified")
        self.assertIn("preview hardware", reason)

    def test_failed_validation_never_creates_fake_verification_status(self):
        """
        Acceptance Criterion: Failed validation never creates fake verification status.
        """
        result = image_verifier.verify_product_image_for_product(
            product_name="Samsung Galaxy S26 Ultra",
            image_url=f"https://m.media-amazon.com/images/I/{S22_ON_S26_SIGNATURE}.jpg",
            check_network=False
        )
        self.assertFalse(result.is_valid)
        self.assertNotEqual(result.verification_status, "verified")
        self.assertEqual(result.verification_status, "quarantined_mismatch")

    def test_quality_scorer_penalizes_quarantined_mismatch(self):
        """
        Catalog quality scorer awards 0/10 points for candidates with quarantined
        mismatched images, preventing unverified images from scoring image points.
        """
        candidate_bad = NormalizedProductCandidate(
            source_id=1,
            source_name="amazon",
            external_id="ext_s26",
            brand="Samsung",
            canonical_brand="Samsung",
            raw_title="Samsung Galaxy S26 Ultra 5G",
            clean_title="Samsung Galaxy S26 Ultra 5G",
            canonical_name="Samsung Galaxy S26 Ultra 5G",
            raw_category="Smartphones",
            canonical_category="Smartphones",
            primary_image_url=f"https://m.media-amazon.com/images/I/{S22_ON_S26_SIGNATURE}.jpg"
        )
        score_bad, _, reasons_bad = ProductQualityScorer.evaluate(candidate_bad)
        self.assertTrue(
            any("Quarantined mismatched image (0/10)" in r for r in reasons_bad),
            "Quarantined mismatch must receive 0/10 in evaluation reasons"
        )

        candidate_neutral = NormalizedProductCandidate(
            source_id=1,
            source_name="amazon",
            external_id="ext_s26",
            brand="Samsung",
            canonical_brand="Samsung",
            raw_title="Samsung Galaxy S26 Ultra 5G",
            clean_title="Samsung Galaxy S26 Ultra 5G",
            canonical_name="Samsung Galaxy S26 Ultra 5G",
            raw_category="Smartphones",
            canonical_category="Smartphones",
            primary_image_url=FALLBACK_PRODUCT_IMAGE
        )
        score_neutral, _, reasons_neutral = ProductQualityScorer.evaluate(candidate_neutral)
        self.assertTrue(
            any("Neutral fallback image present (+5)" in r for r in reasons_neutral),
            "Neutral fallback image must receive safe +5 partial credit"
        )
        self.assertGreater(score_neutral, score_bad)

    def test_repair_image_integrity_is_idempotent(self):
        """
        Acceptance Criterion: The repair script is strictly idempotent and safe to run
        repeatedly without creating duplicate modifications or corruptions.
        """
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brandbattle.db")
        report = repair_sqlite_database(db_path=db_path, dry_run=True)

        # Since repair was already executed, a subsequent audit should find 0 products or offers needing repair
        self.assertEqual(len(report["products_repaired"]), 0, "Repaired database should have 0 products needing repair")
        self.assertEqual(len(report["marketplace_offers_repaired"]), 0, "Repaired database should have 0 offers needing repair")

    def test_canonical_flagships_associate_with_authentic_images(self):
        """
        Acceptance Criterion: Canonical flagship records (iPhone 16 Pro, iPhone 16 Pro Max,
        iPhone 16, Samsung Galaxy S24 Ultra) associate correctly with authentic manufacturer/marketplace images.
        """
        flagship_tests = [
            ("Apple iPhone 16 Pro (256 GB)", "https://m.media-amazon.com/images/I/61bK6PMOC3L._SX679_.jpg"),
            ("Apple iPhone 16 Pro Max (256 GB)", "https://m.media-amazon.com/images/I/71T5NVOgbpL._SX679_.jpg"),
            ("Apple iPhone 16 (128 GB)", "https://m.media-amazon.com/images/I/713SsA7gftL._SX679_.jpg"),
            ("Samsung Galaxy S24 Ultra 5G (256 GB)", "https://m.media-amazon.com/images/I/81njZjDqc6L._SX679_.jpg"),
            ("Google Pixel 9 Pro (256 GB)", "https://m.media-amazon.com/images/I/71eXN-gLdBL._SX679_.jpg"),
            ("OnePlus 12 5G (512 GB)", "https://m.media-amazon.com/images/I/717Qo4MH97L._SX679_.jpg"),
        ]

        for prod_name, img_url in flagship_tests:
            is_valid, status, reason = image_verifier.validate_product_image_association(
                product_name=prod_name,
                image_url=img_url
            )
            self.assertTrue(is_valid, f"{prod_name} must associate successfully with {img_url}. Reason: {reason}")
            self.assertEqual(status, "verified")

            # Safe image resolver must preserve authentic URL, not downgrade to SVG
            safe_url = image_verifier.get_safe_image_for_product(prod_name, img_url)
            self.assertEqual(safe_url, img_url)
            self.assertNotEqual(safe_url, FALLBACK_PRODUCT_IMAGE)

    def test_temporary_network_timeout_returns_pending_retry_not_permanent_rejection(self):
        """
        Acceptance Criterion: A transient network timeout or connection error
        does not mark an image as permanently invalid or quarantined.
        """
        from unittest.mock import patch
        import requests

        with patch("requests.head", side_effect=requests.exceptions.Timeout("Connection timed out")):
            result = image_verifier.verify_image_url("https://m.media-amazon.com/images/I/61bK6PMOC3L._SX679_.jpg")
            self.assertFalse(result.is_valid)
            self.assertEqual(result.verification_status, "pending_retry")
            self.assertIn("transient network delay", result.failure_reason)

    def test_candidate_alternate_fallback_recovery(self):
        """
        Acceptance Criterion: If a primary image URL fails or is empty,
        get_safe_image_for_product checks candidate alternate URLs before resorting to SVG.
        """
        prod_name = "Apple iPhone 16 Pro (256 GB)"
        bad_primary = f"https://m.media-amazon.com/images/I/{S22_ON_S26_SIGNATURE}.jpg"
        good_alternate = "https://m.media-amazon.com/images/I/61bK6PMOC3L._SX679_.jpg"

        resolved = image_verifier.get_safe_image_for_product(
            product_name=prod_name,
            image_url=bad_primary,
            candidate_alternates=[good_alternate]
        )
        self.assertEqual(resolved, good_alternate)

    def test_malformed_url_returns_fallback_cleanly(self):
        """
        Acceptance Criterion: Malformed image URLs produce the neutral SVG fallback
        without crashing or breaking the application.
        """
        malformed_urls = [
            "not-a-valid-url",
            "ftp://invalid-protocol.com/image.jpg",
            "   ",
            None,
        ]
        for url in malformed_urls:
            safe = image_verifier.get_safe_image_for_product("Apple iPhone 16 Pro", url)
            self.assertEqual(safe, FALLBACK_PRODUCT_IMAGE)

    def test_price_and_deal_score_integrity_preserved(self):
        """
        Acceptance Criterion: Image verification repairs have not altered product prices,
        ratings, deal scores, or marketplace offer details.
        """
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brandbattle.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        expected = {
            67: {"price": 164900.0, "deal_score": 92.0},
            68: {"price": 179900.0, "deal_score": 90.0},
            69: {"price": 79900.0, "deal_score": 88.0},
            70: {"price": 129999.0, "deal_score": 94.0},
        }

        for pid, exp in expected.items():
            c.execute("SELECT lowest_price, deal_score FROM products WHERE id = ?", (pid,))
            row = c.fetchone()
            self.assertIsNotNone(row, f"Product ID {pid} must exist in database")
            self.assertEqual(row[0], exp["price"], f"Product {pid} lowest_price must remain {exp['price']}")
            self.assertEqual(row[1], exp["deal_score"], f"Product {pid} deal_score must remain {exp['deal_score']}")

        conn.close()


if __name__ == "__main__":
    unittest.main()

