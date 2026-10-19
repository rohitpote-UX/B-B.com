import unittest
import json
import os
import re

class TestCatalogDataQualitySuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        demo_path = os.path.join(os.path.dirname(__file__), "..", "frontend-next", "src", "data", "demoData.js")
        if not os.path.exists(demo_path):
            raise unittest.SkipTest(f"demoData.js not found at {demo_path}")

        with open(demo_path, "r", encoding="utf-8") as f:
            content = f.read()

        start_match = re.search(r"export const PRODUCTS = \[", content)
        if not start_match:
            raise ValueError("Could not find export const PRODUCTS")
        start_pos = start_match.end() - 1

        end_match = re.search(r"\n\]\s*\n\s*export const", content[start_pos:])
        end_pos = start_pos + end_match.start() + 2

        json_str = content[start_pos:end_pos]
        cls.products = json.loads(json_str)

    def test_01_currency_consistency(self):
        """Invariant: Every product in the India catalog must use INR currency."""
        for p in self.products:
            self.assertEqual(p.get("currency"), "INR", f"Product ID {p.get('id')} has non-INR currency: {p.get('currency')}")

    def test_02_no_zero_or_negative_prices(self):
        """Invariant: Prices must be strictly positive numbers."""
        for p in self.products:
            best_price = p.get("bestPrice", 0)
            orig_price = p.get("originalPrice", 0)
            self.assertGreater(best_price, 0, f"Product ID {p.get('id')} has non-positive bestPrice: {best_price}")
            self.assertGreater(orig_price, 0, f"Product ID {p.get('id')} has non-positive originalPrice: {orig_price}")
            self.assertGreaterEqual(orig_price, best_price, f"Product ID {p.get('id')} has originalPrice < bestPrice")

    def test_03_brand_integrity_no_substring_corruption(self):
        """Invariant: Brand resolution must be deterministic and free from naive substring bleed."""
        for p in self.products:
            name_lower = p.get("name", "").lower()
            brand = p.get("brand", "")

            # Vivobooks must be ASUS, not Vivo
            if "vivobook" in name_lower:
                self.assertEqual(brand, "ASUS", f"Vivobook misclassified as {brand}: {p.get('name')}")

            # Zenbooks must be ASUS
            if "zenbook" in name_lower:
                self.assertEqual(brand, "ASUS", f"Zenbook misclassified as {brand}: {p.get('name')}")

            # Canon cameras must be Canon, not Xiaomi
            if "canon" in name_lower and not any(k in name_lower for k in ["for canon", "lens"]):
                if p.get("category") == "Cameras":
                    self.assertEqual(brand, "Canon", f"Canon camera misclassified as {brand}: {p.get('name')}")

            # Nikon cameras must be Nikon, not Xiaomi
            if "nikon" in name_lower and not any(k in name_lower for k in ["for nikon"]):
                if p.get("category") == "Cameras":
                    self.assertEqual(brand, "Nikon", f"Nikon camera misclassified as {brand}: {p.get('name')}")

            # EvoFox controllers must not be Sony
            if "evofox" in name_lower:
                self.assertEqual(brand, "EVOFOX", f"EvoFox product misclassified as {brand}: {p.get('name')}")

    def test_04_no_keyword_stuffed_spam_listings(self):
        """Invariant: Keyword-stuffed junk listings must be purged from the catalog."""
        for p in self.products:
            name_lower = p.get("name", "").lower()
            self.assertFalse(
                re.search(r"\btreadmill\b.*\bheadset", name_lower),
                f"Spam listing found in catalog: {p.get('name')}"
            )

    def test_05_deal_score_bounded_and_non_arbitrary(self):
        """Invariant: Deal scores must be within realistic bounds [30, 95] and anomalies capped."""
        for p in self.products:
            score = p.get("dealScore")
            self.assertIsNotNone(score, f"Product ID {p.get('id')} is missing dealScore")
            self.assertGreaterEqual(score, 30, f"Product ID {p.get('id')} has score < 30: {score}")
            self.assertLessEqual(score, 95, f"Product ID {p.get('id')} has score > 95: {score}")

            # If marked as anomaly, score must be capped at 45
            if p.get("is_anomaly"):
                self.assertLessEqual(score, 45, f"Anomaly product ID {p.get('id')} received inflated score: {score}")

    def test_06_no_speculative_release_years(self):
        """Invariant: Released products must not have speculative future release years."""
        for p in self.products:
            year = p.get("releaseYear")
            if year:
                self.assertLessEqual(year, 2025, f"Product ID {p.get('id')} has speculative future year: {year}")

    def test_07_no_speculative_tags(self):
        """Invariant: Tags must not contain fake futuristic placeholder names."""
        for p in self.products:
            tags = p.get("tags", [])
            for t in tags:
                self.assertFalse(
                    re.search(r"(?i)\b(?:iphone 18|galaxy s26|oneplus 15)\b", t),
                    f"Product ID {p.get('id')} has speculative tag: {t}"
                )

if __name__ == "__main__":
    unittest.main()
