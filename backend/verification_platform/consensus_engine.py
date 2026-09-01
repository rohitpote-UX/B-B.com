"""
Brand Battle — Consensus Engine
Calculates weighted multi-source consensus values and detects outlier claims.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
from verification_platform.source_trust_engine import source_trust_engine


class ConsensusEngine:
    """Calculates consensus value and confidence score from multiple data source claims."""

    def calculate_consensus(
        self,
        spec_name: str,
        source_claims: Dict[str, Any]  # source_id -> claimed_value
    ) -> Tuple[Any, float, List[str]]:
        """
        Returns (consensus_value, confidence_score, rejected_outliers).
        """
        if not source_claims:
            return (None, 0.0, [])

        if len(source_claims) == 1:
            source_id, val = list(source_claims.items())[0]
            weight = source_trust_engine.get_effective_weight(source_id)
            return (val, round(weight * 95.0, 1), [])

        # Weighted voting by value
        value_weights: Dict[Any, float] = defaultdict(float)
        value_sources: Dict[Any, List[str]] = defaultdict(list)

        for source_id, val in source_claims.items():
            normalized_val = str(val).strip()
            weight = source_trust_engine.get_effective_weight(source_id)
            value_weights[normalized_val] += weight
            value_sources[normalized_val].append(source_id)

        # Find value with highest cumulative trust weight
        best_value_str = max(value_weights, key=value_weights.get)
        best_weight = value_weights[best_value_str]
        total_weight = sum(value_weights.values())

        # Determine rejected outliers
        rejected_outliers = []
        for val_str, sources in value_sources.items():
            if val_str != best_value_str:
                rejected_outliers.extend(sources)

        # Calculate confidence score (0 - 100%)
        agreeing_sources_count = len(value_sources[best_value_str])
        weight_ratio = best_weight / total_weight if total_weight > 0 else 1.0
        
        # High-trust source agreement bonus
        base_confidence = weight_ratio * 102.0
        diversity_bonus = min(15.0, agreeing_sources_count * 4.5)

        confidence = round(min(99.9, base_confidence + diversity_bonus), 1)

        # Return original typed value if available
        original_value = None
        for s_id, v in source_claims.items():
            if str(v).strip() == best_value_str:
                original_value = v
                break

        return (original_value or best_value_str, confidence, rejected_outliers)


consensus_engine = ConsensusEngine()
