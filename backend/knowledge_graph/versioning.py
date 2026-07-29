"""
Brand Battle - Master Product Versioning Engine
Manages immutable version history, diff comparison, and rollback operations for MasterProducts.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
import logging

import models
from knowledge_graph.observability import log_audit_event

logger = logging.getLogger("brandbattle.kg.versioning")


class VersionManager:
    """Handles immutable snapshotting, diffing, and rollback of MasterProducts."""

    def create_version_snapshot(
        self,
        master: models.MasterProduct,
        changed_fields: List[str],
        source_of_change: str = "system",
        updated_by: str = "system",
        change_reason: Optional[str] = None,
        db: Session = None,
    ) -> models.MasterProductVersion:
        """
        Creates an immutable MasterProductVersion snapshot when significant changes occur.
        Increments master.version counter.
        """
        # Fetch previous version ID
        prev_version = (
            db.query(models.MasterProductVersion)
            .filter(models.MasterProductVersion.master_product_id == master.id)
            .order_by(desc(models.MasterProductVersion.version_number))
            .first()
        )
        prev_id = prev_version.id if prev_version else None

        current_ver_num = master.version or 1

        # Extract attributes & tags as JSON for snapshot
        attributes_data = [
            {"name": a.attribute_name, "value": a.attribute_value, "type": a.attribute_type}
            for a in master.attributes
        ] if master.attributes else []

        tags_data = [
            {"tag": t.tag, "type": t.tag_type}
            for t in master.tags
        ] if master.tags else []

        snapshot = models.MasterProductVersion(
            master_product_id=master.id,
            version_number=current_ver_num,
            canonical_name=master.canonical_name,
            description=master.description,
            primary_image_url=master.primary_image_url,
            category_id=master.category_id,
            brand_id=master.brand_id,
            specifications=master.specifications,
            features=master.features,
            images=master.images,
            attributes_json=attributes_data,
            ai_summary=master.ai_summary,
            search_metadata_json={
                "boost_score": master.search_metadata.boost_score if master.search_metadata else 1.0,
                "synonyms": master.search_metadata.synonyms if master.search_metadata else [],
            } if master.search_metadata else None,
            tags_json=tags_data,
            changed_fields=changed_fields,
            source_of_change=source_of_change,
            updated_by=updated_by,
            change_reason=change_reason,
            previous_version_id=prev_id,
        )

        db.add(snapshot)

        # Increment master version number for next modification
        master.version = current_ver_num + 1

        db.flush()
        logger.info(f"📸 Version snapshot v{current_ver_num} created for Master {master.id}")
        return snapshot

    def get_version_history(self, master_id: int, db: Session) -> List[Dict[str, Any]]:
        """Returns ordered list of historical versions for a MasterProduct."""
        versions = (
            db.query(models.MasterProductVersion)
            .filter(models.MasterProductVersion.master_product_id == master_id)
            .order_by(desc(models.MasterProductVersion.version_number))
            .all()
        )

        return [
            {
                "version_id": v.id,
                "version_number": v.version_number,
                "canonical_name": v.canonical_name,
                "changed_fields": v.changed_fields,
                "source_of_change": v.source_of_change,
                "updated_by": v.updated_by,
                "change_reason": v.change_reason,
                "created_at": str(v.created_at),
            }
            for v in versions
        ]

    def compare_versions(
        self,
        version_id_1: int,
        version_id_2: int,
        db: Session
    ) -> Dict[str, Any]:
        """Compares two historical MasterProductVersion records side-by-side."""
        v1 = db.query(models.MasterProductVersion).filter(models.MasterProductVersion.id == version_id_1).first()
        v2 = db.query(models.MasterProductVersion).filter(models.MasterProductVersion.id == version_id_2).first()

        if not v1 or not v2:
            return {"error": "One or both versions not found"}

        diff = {}
        fields = [
            "canonical_name", "description", "primary_image_url",
            "category_id", "brand_id", "specifications", "features",
            "images", "ai_summary"
        ]

        for field in fields:
            val1 = getattr(v1, field)
            val2 = getattr(v2, field)
            if val1 != val2:
                diff[field] = {"version_v1": val1, "version_v2": val2}

        return {
            "v1": {"version_number": v1.version_number, "created_at": str(v1.created_at)},
            "v2": {"version_number": v2.version_number, "created_at": str(v2.created_at)},
            "differences": diff
        }

    def rollback_to_version(
        self,
        master_id: int,
        target_version_number: int,
        actor: str = "admin",
        db: Session = None,
    ) -> Tuple[bool, str]:
        """
        Rolls back a MasterProduct to a previous version snapshot.
        Creates a new version record documenting the rollback action.
        """
        master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
        if not master:
            return False, "Master product not found"

        target_ver = (
            db.query(models.MasterProductVersion)
            .filter(
                models.MasterProductVersion.master_product_id == master_id,
                models.MasterProductVersion.version_number == target_version_number
            )
            .first()
        )

        if not target_ver:
            return False, f"Target version {target_version_number} not found"

        prev_snapshot = {
            "canonical_name": master.canonical_name,
            "description": master.description,
            "specifications": master.specifications,
        }

        # Apply target snapshot data
        master.canonical_name = target_ver.canonical_name
        master.description = target_ver.description
        master.primary_image_url = target_ver.primary_image_url
        if target_ver.brand_id:
            master.brand_id = target_ver.brand_id
        if target_ver.category_id:
            master.category_id = target_ver.category_id
        if target_ver.specifications:
            master.specifications = target_ver.specifications
        if target_ver.features:
            master.features = target_ver.features
        if target_ver.images:
            master.images = target_ver.images
        if target_ver.ai_summary:
            master.ai_summary = target_ver.ai_summary

        # Record snapshot of the rollback
        self.create_version_snapshot(
            master=master,
            changed_fields=["rollback"],
            source_of_change="rollback",
            updated_by=actor,
            change_reason=f"Rollback to version {target_version_number}",
            db=db
        )

        # Audit log
        log_audit_event(
            db=db,
            entity_type="master_product",
            entity_id=master_id,
            action="rollback",
            previous_value=prev_snapshot,
            new_value={"canonical_name": master.canonical_name},
            reason=f"Rollback to v{target_version_number}",
            actor=actor
        )

        db.flush()
        return True, f"Successfully rolled back to version {target_version_number}"


version_manager = VersionManager()
