"""
Brand Battle — SEO Platform Repository Layer
Database access layer following the Repository Pattern for cached metadata and sitemap records.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from seo_platform.models import SeoMetadataRecord


class SeoPlatformRepository:
    """Repository managing database access for the SEO Publishing Platform."""

    def get_cached_metadata(self, db: Session, canonical_slug: str) -> Optional[SeoMetadataRecord]:
        """Fetch cached SEO metadata record."""
        return db.query(SeoMetadataRecord).filter(SeoMetadataRecord.canonical_slug == canonical_slug).first()

    def record_metadata(
        self,
        db: Session,
        canonical_slug: str,
        product1_id: int,
        product2_id: int,
        title: str,
        meta_description: str,
        canonical_url: str,
        open_graph: Dict[str, Any],
        json_ld: Dict[str, Any],
    ) -> SeoMetadataRecord:
        """Cache SEO metadata record."""
        rec = self.get_cached_metadata(db, canonical_slug)
        if not rec:
            rec = SeoMetadataRecord(
                canonical_slug=canonical_slug,
                product1_id=product1_id,
                product2_id=product2_id,
                title=title,
                meta_description=meta_description,
                canonical_url=canonical_url,
                open_graph_json=open_graph,
                json_ld_schema_json=json_ld,
            )
            db.add(rec)
        else:
            rec.title = title
            rec.meta_description = meta_description
            rec.canonical_url = canonical_url
            rec.open_graph_json = open_graph
            rec.json_ld_schema_json = json_ld
        db.commit()
        db.refresh(rec)
        return rec


# Singleton
seo_repo = SeoPlatformRepository()
