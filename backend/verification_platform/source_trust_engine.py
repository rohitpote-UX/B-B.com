"""
Brand Battle — Source Trust Engine
Dynamically adjusts source trust scores based on historical consensus accuracy.
"""

from typing import Dict
from verification_platform.source_registry import source_registry


class SourceTrustEngine:
    """Calculates and updates source reliability scores dynamically."""

    def evaluate_verification_outcome(
        self,
        source_id: str,
        agreed_with_consensus: bool,
        confidence_delta: float = 1.0
    ) -> float:
        """
        Adjusts a source's trust score based on whether its claim aligned with consensus.
        """
        source = source_registry.get_source(source_id)
        if not source:
            return 50.0

        current_score = source.trust_score
        
        if agreed_with_consensus:
            # Reward source slightly (max 100)
            adjustment = min(0.5, (100.0 - current_score) * 0.05)
            new_score = current_score + adjustment
        else:
            # Penalize outlier claim (min 10)
            adjustment = max(1.0, current_score * 0.03)
            new_score = current_score - adjustment

        source_registry.update_trust_score(source_id, new_score)
        return new_score

    def get_effective_weight(self, source_id: str) -> float:
        """Returns normalized 0.0 - 1.0 weight for weighted voting calculations."""
        source = source_registry.get_source(source_id)
        if not source:
            return 0.5
        return round(source.trust_score / 100.0, 4)


source_trust_engine = SourceTrustEngine()
