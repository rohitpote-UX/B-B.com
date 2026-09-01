"""
Brand Battle — Conflict Resolution Engine
Logs, tracks, and resolves specification discrepancies across sources.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from verification_platform.schemas import ConflictRecord
from verification_platform.source_trust_engine import source_trust_engine
from verification_platform.variant_detector import variant_detector


class ConflictResolutionEngine:
    """Manages conflict resolution and audit logging for disputed specs."""

    def __init__(self):
        self._conflict_history: List[ConflictRecord] = []

    def resolve_conflict(
        self,
        spec_name: str,
        claims: Dict[str, Any],
        consensus_value: Any,
        confidence_score: float,
        rejected_sources: List[str]
    ) -> ConflictRecord:
        """
        Creates and stores an immutable conflict resolution record.
        """
        strategy = "Weighted Source Voting & Outlier Rejection"
        
        # Check if regional variant marker applies
        if len(claims) >= 2:
            vals = list(claims.values())
            if variant_detector.is_chipset_variant(spec_name, vals[0], vals[1]):
                strategy = "Regional Chipset Variant Detected"

        record = ConflictRecord(
            conflict_id=f"cnf_{uuid.uuid4().hex[:8]}",
            spec_name=spec_name,
            disputed_values=claims,
            resolved_value=consensus_value,
            resolution_strategy=strategy,
            confidence_score=confidence_score,
            timestamp=datetime.utcnow()
        )

        self._conflict_history.append(record)

        # Update source trust scores based on outlier rejection
        for source_id in claims.keys():
            agreed = source_id not in rejected_sources
            source_trust_engine.evaluate_verification_outcome(source_id, agreed_with_consensus=agreed)

        return record

    def get_conflict_history(self, limit: int = 50) -> List[ConflictRecord]:
        return self._conflict_history[-limit:]


conflict_resolution_engine = ConflictResolutionEngine()
