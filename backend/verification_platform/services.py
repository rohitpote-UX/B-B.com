"""
Brand Battle — Verification Services
High-level service interface for PVTP platform operations.
"""

from typing import Dict, List, Any, Optional
from verification_platform.verification_pipeline import verification_pipeline
from verification_platform.schemas import (
    VerificationSummaryResponse,
    TrustScoreResponse,
    SourceInfo,
    VerificationMetricsResponse,
    CommunitySuggestionRequest,
    AuditLogRecord
)
from verification_platform.source_registry import source_registry
from verification_platform.verification_metrics import verification_metrics_aggregator
from verification_platform.audit_logger import audit_logger
from verification_platform.evidence_repository import evidence_repository
from verification_platform.models import CommunitySuggestionRecord


class VerificationService:
    """High-level service providing clean boundaries for PVTP operations."""

    def get_verification_summary(
        self,
        product_id: int,
        product_name: str = "Sony WH-1000XM5 Wireless Headphones",
        specs: Optional[Dict[str, Any]] = None
    ) -> VerificationSummaryResponse:
        default_specs = specs or {
            "ANC Technology": "30dB Hybrid Dual Noise Sensor",
            "Battery Life": "30 Hours (ANC On)",
            "Weight": "250g",
            "Driver Size": "30mm Carbon Fiber",
            "Bluetooth": "v5.2 (LDAC, AAC, SBC)"
        }
        return verification_pipeline.run_pipeline(
            product_id=product_id,
            product_name=product_name,
            specs=default_specs
        )

    def get_sources(self) -> List[SourceInfo]:
        return source_registry.list_sources()

    def get_metrics(self) -> VerificationMetricsResponse:
        return verification_metrics_aggregator.get_platform_metrics()

    def submit_community_suggestion(
        self,
        req: CommunitySuggestionRequest
    ) -> Dict[str, Any]:
        record = CommunitySuggestionRecord(
            product_id=req.product_id,
            spec_name=req.spec_name,
            suggested_value=req.suggested_value,
            evidence_url_or_text=req.evidence_url_or_text,
            contributor_email=req.contributor_email
        )
        audit_logger.log_action(
            product_id=req.product_id,
            action="COMMUNITY_SUGGESTION_SUBMITTED",
            actor=record.contributor_email,
            details={
                "suggestion_id": record.suggestion_id,
                "spec_name": req.spec_name,
                "suggested_value": req.suggested_value
            }
        )
        return {
            "status": "success",
            "suggestion_id": record.suggestion_id,
            "message": "Suggestion queued for reviewer validation."
        }

    def get_audit_logs(self, product_id: Optional[int] = None) -> List[AuditLogRecord]:
        return audit_logger.get_audit_trail(product_id=product_id)


verification_service = VerificationService()
