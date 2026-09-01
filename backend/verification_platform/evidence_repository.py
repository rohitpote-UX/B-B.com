"""
Brand Battle — Evidence Repository
Stores immutable cryptographic evidence records and hashes for every claim.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from verification_platform.schemas import EvidenceReference


class EvidenceRepository:
    """Stores SHA-256 evidence records proving verification claims."""

    def __init__(self):
        self._evidence_store: Dict[str, EvidenceReference] = {}

    def generate_hash(self, product_id: int, spec_name: str, source_id: str, claim_value: Any) -> str:
        """Generates SHA-256 evidence hash from claim parameters."""
        payload = f"{product_id}:{spec_name}:{source_id}:{str(claim_value)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record_evidence(
        self,
        product_id: int,
        spec_name: str,
        source_id: str,
        source_name: str,
        claim_value: Any,
        trust_weight: float
    ) -> EvidenceReference:
        """Creates and indexes a verified evidence record."""
        ev_hash = self.generate_hash(product_id, spec_name, source_id, claim_value)
        evidence_id = f"ev_{uuid.uuid4().hex[:8]}"

        ref = EvidenceReference(
            evidence_id=evidence_id,
            spec_name=spec_name,
            source_id=source_id,
            source_name=source_name,
            raw_claim_value=claim_value,
            evidence_hash=ev_hash,
            verified_at=datetime.now(timezone.utc),
            trust_weight=trust_weight
        )

        self._evidence_store[evidence_id] = ref
        return ref

    def get_evidence_by_hash(self, ev_hash: str) -> Optional[EvidenceReference]:
        for ref in self._evidence_store.values():
            if ref.evidence_hash == ev_hash:
                return ref
        return None

    def list_product_evidence(self, limit: int = 100) -> List[EvidenceReference]:
        return list(self._evidence_store.values())[-limit:]


evidence_repository = EvidenceRepository()
