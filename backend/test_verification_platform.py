"""
Brand Battle — Verification Platform Test Suite
Tests source registry, consensus engine, conflict resolution, evidence hashing, trust score calculation, and API router endpoints.
"""

import unittest
import sys
import os

# Add backend directory to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from fastapi.testclient import TestClient
from main import app
from verification_platform.source_registry import source_registry
from verification_platform.consensus_engine import consensus_engine
from verification_platform.conflict_resolution import conflict_resolution_engine
from verification_platform.evidence_repository import evidence_repository
from verification_platform.trust_score import trust_score_engine
from verification_platform.variant_detector import variant_detector
from verification_platform.freshness_engine import freshness_engine

client = TestClient(app)


class TestVerificationPlatform(unittest.TestCase):

    def test_source_registry(self):
        sources = source_registry.list_sources()
        self.assertGreaterEqual(len(sources), 15)
        fcc = source_registry.get_source("src_fcc")
        self.assertIsNotNone(fcc)
        self.assertEqual(fcc.trust_score, 99.0)

    def test_consensus_engine_and_outliers(self):
        claims = {
            "src_official_pdf": "2600 nits",
            "src_displaymate": "2600 nits",
            "src_notebookcheck": "2600 nits",
            "src_amazon": "3200 nits"  # Outlier claim
        }
        val, confidence, outliers = consensus_engine.calculate_consensus("Display Brightness", claims)
        self.assertEqual(val, "2600 nits")
        self.assertGreater(confidence, 90.0)
        self.assertIn("src_amazon", outliers)

    def test_variant_detector(self):
        region = variant_detector.detect_variant("Samsung Galaxy S24 Ultra (BIS Certified)", {"Price": "₹119,999"})
        self.assertEqual(region, "INDIA")

    def test_evidence_repository_hashing(self):
        ref = evidence_repository.record_evidence(
            product_id=1,
            spec_name="Battery",
            source_id="src_official_pdf",
            source_name="Official Whitepaper",
            claim_value="5000 mAh",
            trust_weight=1.0
        )
        self.assertIsNotNone(ref.evidence_hash)
        self.assertEqual(len(ref.evidence_hash), 64)

    def test_api_verification_endpoints(self):
        res = client.get("/api/verification/sources")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()), 15)

        res = client.get("/api/verification/summary/1")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["product_id"], 1)
        self.assertGreaterEqual(data["trust_score"]["trust_score"], 80.0)
        self.assertGreater(len(data["specifications_confidence"]), 0)

        res = client.get("/api/verification/metrics")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["total_products_verified"], 1000)


if __name__ == "__main__":
    unittest.main()
