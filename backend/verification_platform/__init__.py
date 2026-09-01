"""
Brand Battle — Enterprise Product Verification & Trust Platform (PVTP)
Exports main API router and core service definitions.
"""

from verification_platform.api import router as verification_router
from verification_platform.services import verification_service
from verification_platform.product_verifier import product_verifier
from verification_platform.source_registry import source_registry

__all__ = [
    "verification_router",
    "verification_service",
    "product_verifier",
    "source_registry",
]
