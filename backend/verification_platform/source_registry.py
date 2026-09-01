"""
Brand Battle — Source Registry
Manages registration, metadata, and default trust weights for all data sources.
"""

from typing import Dict, List, Optional
from datetime import datetime
from verification_platform.schemas import SourceInfo


DEFAULT_SOURCES: List[SourceInfo] = [
    SourceInfo(
        source_id="src_official_pdf",
        name="Official Manufacturer Whitepaper / PDF",
        source_type="official_cert",
        trust_score=100.0,
        country="GLOBAL",
        update_frequency_hours=12,
        average_accuracy=99.9,
        historical_reliability=99.9,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_fcc",
        name="FCC Regulatory Certification",
        source_type="official_cert",
        trust_score=99.0,
        country="USA",
        update_frequency_hours=24,
        average_accuracy=99.5,
        historical_reliability=99.5,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_bis",
        name="Bureau of Indian Standards (BIS)",
        source_type="official_cert",
        trust_score=98.5,
        country="INDIA",
        update_frequency_hours=24,
        average_accuracy=99.0,
        historical_reliability=99.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_mfr_site",
        name="Official Brand Website Specs",
        source_type="manufacturer",
        trust_score=98.0,
        country="GLOBAL",
        update_frequency_hours=12,
        average_accuracy=98.5,
        historical_reliability=98.5,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_rtings",
        name="RTINGS Hardware Test Lab",
        source_type="review_lab",
        trust_score=97.5,
        country="CANADA",
        update_frequency_hours=48,
        average_accuracy=97.8,
        historical_reliability=97.5,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_displaymate",
        name="DisplayMate Optics Lab",
        source_type="review_lab",
        trust_score=97.0,
        country="USA",
        update_frequency_hours=72,
        average_accuracy=97.5,
        historical_reliability=97.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_notebookcheck",
        name="Notebookcheck Hardware Benchmarks",
        source_type="review_lab",
        trust_score=96.5,
        country="GERMANY",
        update_frequency_hours=48,
        average_accuracy=96.8,
        historical_reliability=96.5,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_gsmarena",
        name="GSMArena Spec Database",
        source_type="review_lab",
        trust_score=95.0,
        country="GLOBAL",
        update_frequency_hours=12,
        average_accuracy=95.5,
        historical_reliability=95.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_dxomark",
        name="DXOMARK Imaging & Audio Lab",
        source_type="review_lab",
        trust_score=94.5,
        country="FRANCE",
        update_frequency_hours=48,
        average_accuracy=95.0,
        historical_reliability=94.5,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_amazon",
        name="Amazon Product API",
        source_type="retailer",
        trust_score=84.0,
        country="GLOBAL",
        update_frequency_hours=6,
        average_accuracy=85.0,
        historical_reliability=84.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_flipkart",
        name="Flipkart Verified Listing",
        source_type="retailer",
        trust_score=83.0,
        country="INDIA",
        update_frequency_hours=6,
        average_accuracy=84.0,
        historical_reliability=83.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_croma",
        name="Croma Authorized Retailer",
        source_type="retailer",
        trust_score=85.0,
        country="INDIA",
        update_frequency_hours=12,
        average_accuracy=86.0,
        historical_reliability=85.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_reliance_digital",
        name="Reliance Digital Store",
        source_type="retailer",
        trust_score=84.5,
        country="INDIA",
        update_frequency_hours=12,
        average_accuracy=85.5,
        historical_reliability=84.5,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_unverified_seller",
        name="Third-Party Marketplace Seller Listing",
        source_type="retailer",
        trust_score=61.0,
        country="GLOBAL",
        update_frequency_hours=24,
        average_accuracy=62.0,
        historical_reliability=61.0,
        last_sync=datetime.utcnow()
    ),
    SourceInfo(
        source_id="src_community_verified",
        name="Community Peer-Reviewed Correction",
        source_type="community",
        trust_score=88.0,
        country="GLOBAL",
        update_frequency_hours=24,
        average_accuracy=89.0,
        historical_reliability=88.0,
        last_sync=datetime.utcnow()
    )
]


class SourceRegistry:
    """Singleton registry holding source definitions."""

    def __init__(self):
        self._sources: Dict[str, SourceInfo] = {s.source_id: s for s in DEFAULT_SOURCES}

    def get_source(self, source_id: str) -> Optional[SourceInfo]:
        return self._sources.get(source_id)

    def list_sources(self) -> List[SourceInfo]:
        return list(self._sources.values())

    def update_trust_score(self, source_id: str, new_score: float) -> bool:
        if source_id in self._sources:
            self._sources[source_id].trust_score = max(0.0, min(100.0, new_score))
            self._sources[source_id].last_sync = datetime.utcnow()
            return True
        return False


source_registry = SourceRegistry()
