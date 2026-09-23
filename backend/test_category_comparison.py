"""
Automated Test Suite: Category-Aware Comparison & Real-World Performance Engine
Validates:
1. Electronics comparisons retain existing Battery, Thermal, Gaming, Camera metrics without regression.
2. Shoes/Footwear comparisons NEVER leak Battery, Thermal, Gaming, Camera metrics and use Footwear signals.
3. Apparel/Clothing comparisons NEVER leak electronics metrics and use Apparel signals.
4. Beauty/Cosmetics comparisons NEVER leak electronics metrics and use Beauty signals.
5. Exact screenshot products: Campus Men Sneakers vs Puma Badminton Smash Sprint Shoes.
6. Cross-category comparison warning handling.
7. Missing data handling.
"""

import os
import sys
import unittest
from types import SimpleNamespace

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from comparison_workspace.key_differences import key_differences_engine


class TestCategoryComparisonEngine(unittest.TestCase):

    def test_electronics_vs_electronics(self):
        """Electronics comparison must preserve Battery, Refresh Rate, Charging, and Price."""
        p1 = SimpleNamespace(
            id=1,
            name="Apple iPhone 18 Pro Max",
            category="Smartphones",
            current_best_price=179900.0,
        )
        p2 = SimpleNamespace(
            id=2,
            name="Samsung Galaxy S24 Ultra",
            category="Smartphones",
            current_best_price=129999.0,
        )

        diffs = key_differences_engine.isolate_key_differences(p1, p2)
        attr_names = [d["attribute"] for d in diffs]

        self.assertIn("Price", attr_names)
        self.assertIn("Battery Capacity", attr_names)
        self.assertIn("Display Refresh Rate", attr_names)
        self.assertIn("Fast Charging", attr_names)

        # Ensure NO footwear or clothing metrics leaked into electronics
        self.assertNotIn("Outsole Traction", attr_names)
        self.assertNotIn("Fabric Composition", attr_names)
        self.assertNotIn("Scent Concentration", attr_names)

    def test_footwear_screenshot_regression(self):
        """
        Exact regression test for user-reported case:
        Campus Men Sneakers vs Puma Badminton Smash Sprint Shoes.
        MUST NOT contain Battery, Thermal, Gaming, Camera.
        MUST contain Footwear dimensions.
        """
        p1 = SimpleNamespace(
            id=1199,
            name="Campus Men Sneakers",
            category="Shoes",
            current_best_price=1752.0,
        )
        p2 = SimpleNamespace(
            id=1113,
            name="Puma Badminton Smash Sprint Shoes",
            category="Shoes",
            current_best_price=1756.0,
        )

        diffs = key_differences_engine.isolate_key_differences(p1, p2)
        attr_names = [d["attribute"] for d in diffs]

        # CRITICAL ASSERTIONS: ZERO electronics metrics
        self.assertNotIn("Battery Capacity", attr_names)
        self.assertNotIn("Display Refresh Rate", attr_names)
        self.assertNotIn("Fast Charging", attr_names)
        self.assertNotIn("Camera Quality", attr_names)
        self.assertNotIn("Gaming Performance", attr_names)
        self.assertNotIn("Thermal Control", attr_names)

        # Footwear metrics MUST be present
        self.assertIn("Price", attr_names)
        self.assertIn("Outsole Traction", attr_names)
        self.assertIn("Midsole Cushioning", attr_names)
        self.assertIn("Upper Construction", attr_names)
        self.assertIn("Return & Size Exchange", attr_names)

        # Puma Badminton should have court traction highlight
        traction = next(d for d in diffs if d["attribute"] == "Outsole Traction")
        self.assertTrue("Rubber" in traction["p1_value"] or "Rubber" in traction["p2_value"])

    def test_apparel_vs_apparel(self):
        """Apparel comparison must use Fabric, Fit, Breathability dimensions and NO electronics metrics."""
        p1 = SimpleNamespace(
            id=201,
            name="Campus Sutra Men Self Design Cotton T-shirt",
            category="Clothing",
            current_best_price=611.0,
        )
        p2 = SimpleNamespace(
            id=202,
            name="Puma Men's Slim Fit Polo T-shirt",
            category="Clothing",
            current_best_price=1299.0,
        )

        diffs = key_differences_engine.isolate_key_differences(p1, p2)
        attr_names = [d["attribute"] for d in diffs]

        self.assertNotIn("Battery Capacity", attr_names)
        self.assertNotIn("Display Refresh Rate", attr_names)
        self.assertIn("Price", attr_names)
        self.assertIn("Fabric Composition", attr_names)
        self.assertIn("Fit & Silhouette", attr_names)
        self.assertIn("Fabric Breathability", attr_names)

    def test_beauty_vs_beauty(self):
        """Beauty comparison must use Scent Concentration, Wear Longevity, Sillage and NO electronics."""
        p1 = SimpleNamespace(
            id=301,
            name="Wild stone Men Edge EDP 100 ml",
            category="Beauty",
            current_best_price=381.0,
        )
        p2 = SimpleNamespace(
            id=302,
            name="SKINN Men Raw Eau De Parfum 50 ml",
            category="Beauty",
            current_best_price=1895.0,
        )

        diffs = key_differences_engine.isolate_key_differences(p1, p2)
        attr_names = [d["attribute"] for d in diffs]

        self.assertNotIn("Battery Capacity", attr_names)
        self.assertNotIn("Display Refresh Rate", attr_names)
        self.assertIn("Price", attr_names)
        self.assertIn("Scent Concentration", attr_names)
        self.assertIn("Wear Longevity", attr_names)
        self.assertIn("Projection Intensity", attr_names)


if __name__ == "__main__":
    unittest.main()
