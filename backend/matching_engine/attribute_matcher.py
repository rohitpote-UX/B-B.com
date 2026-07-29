"""
Brand Battle - Attribute Matcher Module
Normalized attribute similarity evaluator (color, material, gender, product_type, variant).
"""

from typing import Dict, Any, Optional


class AttributeMatcher:
    """Evaluates normalized identity attributes between listing and master candidate."""

    def evaluate(self, item_features: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates attribute match score (0.0 to 1.0) with signal breakdown."""
        score = 0.0
        comparisons = 0
        breakdown = {}

        attr_pairs = [
            ("color_family", "color_family", 1.0),
            ("material", "material", 1.0),
            ("gender", "gender", 1.0),
            ("product_type", "product_type", 1.2),
            ("model_series", "model_series", 1.5),
        ]

        for feat_key, cand_key, weight in attr_pairs:
            iv = item_features.get(feat_key)
            cv = candidate.get(cand_key)

            if iv and cv:
                comparisons += weight
                if str(iv).strip().lower() == str(cv).strip().lower():
                    score += weight
                    breakdown[feat_key] = 1.0
                else:
                    breakdown[feat_key] = 0.0

        if comparisons == 0:
            return {"score": 0.5, "explanation": "No overlapping attributes present", "breakdown": {}}

        final_score = round(score / comparisons, 3)
        return {
            "score": final_score,
            "breakdown": breakdown,
            "explanation": f"Attribute match ratio: {final_score:.2f} across {len(breakdown)} signals"
        }


attribute_matcher = AttributeMatcher()
