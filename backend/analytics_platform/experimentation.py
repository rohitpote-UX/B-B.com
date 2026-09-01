"""
Brand Battle — 16. Experimentation Platform Engine
Provides A/B testing infrastructure, variant assignment, and p-value statistical significance calculation.
"""

from typing import Dict, Any, List
import math


class ExperimentationPlatformEngine:
    """Computes A/B testing statistical significance and variant performance."""

    def calculate_statistical_significance(
        self, control_conversions: int, control_total: int, variant_conversions: int, variant_total: int
    ) -> Dict[str, Any]:
        """Compute p-value and statistical significance between variants."""
        p1 = control_conversions / max(1, control_total)
        p2 = variant_conversions / max(1, variant_total)

        p_pool = (control_conversions + variant_conversions) / max(1, (control_total + variant_total))
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / max(1, control_total) + 1 / max(1, variant_total)))

        z_score = (p2 - p1) / se if se > 0 else 0.0
        p_value = round(max(0.001, 1.0 - (0.5 * (1.0 + math.erf(abs(z_score) / math.sqrt(2))))), 4)

        is_significant = p_value < 0.05

        return {
            "control_conversion_rate": round(p1 * 100, 2),
            "variant_conversion_rate": round(p2 * 100, 2),
            "relative_uplift_pct": round(((p2 - p1) / max(0.001, p1)) * 100, 2),
            "z_score": round(z_score, 2),
            "p_value": p_value,
            "is_statistically_significant": is_significant,
        }


# Singleton
experimentation_platform_engine = ExperimentationPlatformEngine()
