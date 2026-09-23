"""
Brand Battle — Product Identity & Variant Resolver
Distinguishes Product Family roots from specific Variant nodes,
links them via ProductRelationship graph edges, and generates stable slugs.
"""

import re
import uuid
import logging
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session

import models
from catalog_engine.schemas import NormalizedProductCandidate

logger = logging.getLogger("brandbattle.catalog.resolver")


class ProductIdentityResolver:
    """
    Resolves product family hierarchies, variant relationships,
    and brand/category database entities.
    """

    @classmethod
    def resolve_brand(cls, canonical_brand_name: str, db: Session) -> models.Brand:
        """Finds or creates canonical Brand model."""
        brand = db.query(models.Brand).filter(models.Brand.name.ilike(canonical_brand_name)).first()
        if not brand:
            slug = re.sub(r"[^a-z0-9]+", "-", canonical_brand_name.lower()).strip("-")
            brand = models.Brand(
                name=canonical_brand_name,
                slug=slug,
                trust_score=7.5,
                is_verified=True,
            )
            db.add(brand)
            db.flush()
        return brand

    @classmethod
    def resolve_category(cls, canonical_category_name: str, db: Session) -> models.Category:
        """Finds or creates canonical Category model."""
        category = db.query(models.Category).filter(models.Category.name.ilike(canonical_category_name)).first()
        if not category:
            slug = re.sub(r"[^a-z0-9]+", "-", canonical_category_name.lower()).strip("-")
            category = models.Category(
                name=canonical_category_name,
                slug=slug,
                description=f"Curated {canonical_category_name} on BrandBattle",
            )
            db.add(category)
            db.flush()
        return category

    @classmethod
    def generate_unique_slug(cls, base_text: str, db: Session) -> str:
        """Generates a stable, unique, SEO-friendly slug."""
        base_slug = re.sub(r"[^a-z0-9]+", "-", base_text.lower()).strip("-")
        if not base_slug:
            base_slug = "product"

        slug = base_slug
        counter = 1
        while db.query(models.MasterProduct).filter(models.MasterProduct.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @classmethod
    def link_variant_relationship(
        cls,
        parent_master_id: int,
        variant_master_id: int,
        variant_attrs: Dict[str, Any],
        db: Session
    ) -> Optional[models.ProductRelationship]:
        """
        Creates bidirectional 'variant' relationship between parent family and variant master.
        """
        if parent_master_id == variant_master_id:
            return None

        # Check existing edge
        existing = db.query(models.ProductRelationship).filter(
            models.ProductRelationship.source_master_id == parent_master_id,
            models.ProductRelationship.target_master_id == variant_master_id,
            models.ProductRelationship.relationship_type == models.RelationshipType.ALTERNATIVE.value
        ).first()

        if existing:
            return existing

        edge = models.ProductRelationship(
            source_master_id=parent_master_id,
            target_master_id=variant_master_id,
            relationship_type="variant",
            confidence=1.0,
            weight=1.0,
            discovery_method="catalog_engine_variant_resolver",
            creation_source="catalog_ingestion",
            signal_breakdown=variant_attrs,
            is_bidirectional=True,
        )
        db.add(edge)
        db.flush()
        return edge
