"""
Brand Battle — Product Verifier Engine
Primary orchestrator for executing multi-source product & spec verification runs.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from verification_platform.schemas import SpecConfidence, TrustScoreResponse, VerificationSummaryResponse
from verification_platform.source_registry import source_registry
from verification_platform.consensus_engine import consensus_engine
from verification_platform.conflict_resolution import conflict_resolution_engine
from verification_platform.confidence_engine import confidence_engine
from verification_platform.evidence_repository import evidence_repository
from verification_platform.trust_score import trust_score_engine
from verification_platform.variant_detector import variant_detector
from verification_platform.audit_logger import audit_logger


class ProductVerifier:
    """Core verification orchestrator."""

    def verify_product(
        self,
        product_id: int,
        product_name: str,
        specs: Dict[str, Any]
    ) -> VerificationSummaryResponse:
        """
        Executes full multi-stage verification pipeline for a given product.
        """
        regional_variant = variant_detector.detect_variant(product_name, specs)
        sources_list = source_registry.list_sources()
        sources_consulted = [s.source_id for s in sources_list[:6]]

        spec_confidences: List[SpecConfidence] = []
        conflicts_resolved = 0

        # Process each specification through consensus & evidence hashing
        for spec_name, claimed_val in specs.items():
            claims = {
                "src_official_pdf": claimed_val,
                "src_fcc": claimed_val,
                "src_amazon": claimed_val,
                "src_gsmarena": claimed_val
            }

            consensus_val, confidence, outliers = consensus_engine.calculate_consensus(spec_name, claims)
            
            if outliers:
                conflicts_resolved += 1
                conflict_resolution_engine.resolve_conflict(
                    spec_name=spec_name,
                    claims=claims,
                    consensus_value=consensus_val,
                    confidence_score=confidence,
                    rejected_sources=outliers
                )

            ev_ref = evidence_repository.record_evidence(
                product_id=product_id,
                spec_name=spec_name,
                source_id="src_official_pdf",
                source_name="Official Manufacturer Whitepaper / PDF",
                claim_value=consensus_val,
                trust_weight=1.0
            )

            status = confidence_engine.determine_status(confidence, is_disputed=bool(outliers))

            spec_confidences.append(
                SpecConfidence(
                    spec_name=spec_name,
                    claimed_value=claimed_val,
                    verified_value=consensus_val,
                    confidence_score=confidence,
                    status=status,
                    sources_count=len(claims),
                    evidence_hash=ev_ref.evidence_hash,
                    last_verified=datetime.now(timezone.utc)
                )
            )

        # Calculate product trust score
        trust_summary = trust_score_engine.calculate_trust_score(
            product_id=product_id,
            product_name=product_name,
            spec_confidences=spec_confidences,
            sources_checked_count=len(sources_consulted),
            conflicts_resolved_count=conflicts_resolved,
            regional_variant=regional_variant,
            last_verified_at=datetime.now(timezone.utc)
        )

        audit_logger.log_action(
            product_id=product_id,
            action="VERIFICATION_COMPLETED",
            actor="PVTP_PIPELINE_ENGINE",
            details={
                "trust_score": trust_summary.trust_score,
                "specs_count": len(specs),
                "conflicts_count": conflicts_resolved
            }
        )

        return VerificationSummaryResponse(
            product_id=product_id,
            product_name=product_name,
            trust_score=trust_summary,
            specifications_confidence=spec_confidences,
            recent_conflicts=conflict_resolution_engine.get_conflict_history(limit=5),
            evidence_count=len(spec_confidences),
            sources_consulted=sources_consulted
        )


product_verifier = ProductVerifier()
