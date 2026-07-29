"""
Brand Battle - Product Quality Verification Engine
Calculates data completeness score (0-100) and enforces threshold quality checks.
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger("brandbattle.quality")


class QualityVerifier:
    """Evaluates data completeness, spec density, and payload quality score."""

    def calculate_quality_score(self, item: Dict[str, Any], matching_confidence: float = 1.0) -> float:
        """
        Calculates quality score (0-100) for product record.
        """
        score = 0.0

        # 1. Specifications completeness (max 30 pts)
        specs = item.get("normalized_specs", item.get("specifications", {}))
        if isinstance(specs, dict):
            spec_count = len(specs)
            score += min(30.0, spec_count * 6.0)

        # 2. Image availability (max 25 pts)
        image_url = item.get("image_url")
        if image_url and str(image_url).startswith("http"):
            score += 25.0

        # 3. Rating & Review metrics (max 20 pts)
        rating = item.get("rating")
        reviews = item.get("total_reviews")
        if rating and rating > 0:
            score += 10.0
        if reviews and reviews > 0:
            score += 10.0

        # 4. Seller credibility & availability (max 15 pts)
        seller = item.get("seller_name")
        if seller:
            score += 10.0
        if item.get("availability", True):
            score += 5.0

        # 5. Matching confidence (max 10 pts)
        score += max(0.0, matching_confidence * 10.0)

        return min(100.0, round(score, 1))

    def verify(self, item: Dict[str, Any], matching_confidence: float = 1.0, min_threshold: float = 50.0) -> Tuple[bool, float, str]:
        """
        Verifies if item satisfies minimum quality threshold.
        Returns: (passes: bool, quality_score: float, reason: str)
        """
        score = self.calculate_quality_score(item, matching_confidence)
        if score < min_threshold:
            reason = f"Quality score {score}/100 is below minimum threshold of {min_threshold}"
            logger.warning(f"Product verification failed: '{item.get('clean_title', item.get('raw_title'))}' - {reason}")
            return False, score, reason

        return True, score, "Quality score verified"
