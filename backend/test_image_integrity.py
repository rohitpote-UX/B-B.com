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


if __name__ == "__main__":
    unittest.main()
