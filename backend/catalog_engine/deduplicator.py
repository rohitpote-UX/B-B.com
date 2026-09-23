"""
Brand Battle — Identifier-First Deduplication Engine
Implements strict matching priority:
1. Valid GTIN / EAN / UPC
2. MPN + Brand
3. Model Number + Brand
4. External Source ID (same source)
5. Strong Normalized Attribute Ensemble
6. Controlled Fuzzy Matching (Candidate only, never auto-merge below 0.98)
Hard Constraint: Products must share compatible categories.
"""

from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
import re
import logging

import models
from catalog_engine.schemas import NormalizedProductCandidate

logger = logging.getLogger("brandbattle.catalog.deduplicator")


class CatalogDeduplicator:
    """
    Resolves product candidate identity against existing MasterProducts
    using strict identifier-first priority.
    """

    AUTO_MATCH_THRESHOLD = 0.98
    REVIEW_THRESHOLD = 0.85

    @classmethod
    def resolve_candidate(
        cls,
        candidate: NormalizedProductCandidate,
        db: Session
    ) -> Tuple[Optional[models.MasterProduct], float, str]:
        """
        Determines if candidate matches an existing MasterProduct.
        Returns: (matched_master: Optional[MasterProduct], match_confidence: float, match_reason: str)
        """
        # 1. Match by Validated GTIN / EAN / UPC (Priority 1)
        if candidate.is_gtin_valid and (candidate.gtin or candidate.ean or candidate.upc):
            identifier = candidate.gtin or candidate.ean or candidate.upc
            # Check global_sku on MasterProduct
            existing_by_sku = db.query(models.MasterProduct).filter(
                models.MasterProduct.global_sku == identifier,
                models.MasterProduct.is_active == True
            ).first()
            if existing_by_sku and cls._is_category_compatible(candidate.canonical_category, existing_by_sku):
                return existing_by_sku, 1.0, f"Exact GTIN match ({identifier})"

            # Check ProductAttribute table
            attr_match = db.query(models.ProductAttribute).filter(
                models.ProductAttribute.attribute_name.in_(["gtin", "ean", "upc"]),
                models.ProductAttribute.attribute_value == identifier
            ).first()
            if attr_match:
                master = db.get(models.MasterProduct, attr_match.master_product_id)
                if master and master.is_active and cls._is_category_compatible(candidate.canonical_category, master):
                    return master, 1.0, f"Attribute GTIN match ({identifier})"

        # 2. Match by MPN + Brand (Priority 2)
        if candidate.mpn and candidate.canonical_brand:
            mpn_clean = candidate.mpn.strip().upper()
            attr_mpn = db.query(models.ProductAttribute).join(
                models.MasterProduct, models.ProductAttribute.master_product_id == models.MasterProduct.id
            ).join(
                models.Brand, models.MasterProduct.brand_id == models.Brand.id
            ).filter(
                models.ProductAttribute.attribute_name == "mpn",
                models.ProductAttribute.attribute_value.ilike(mpn_clean),
                models.Brand.name.ilike(candidate.canonical_brand),
                models.MasterProduct.is_active == True
            ).first()
            if attr_mpn:
                master = db.get(models.MasterProduct, attr_mpn.master_product_id)
                if master and cls._is_category_compatible(candidate.canonical_category, master):
                    return master, 0.99, f"Exact MPN+Brand match ({mpn_clean})"

        # 3. Match by Model Number + Brand (Priority 3)
        if candidate.model_number and candidate.canonical_brand:
            model_num_clean = candidate.model_number.strip().upper()
            existing_model = db.query(models.MasterProduct).join(
                models.Brand, models.MasterProduct.brand_id == models.Brand.id
            ).filter(
                models.MasterProduct.model_name.ilike(model_num_clean),
                models.Brand.name.ilike(candidate.canonical_brand),
                models.MasterProduct.is_active == True
            ).first()
            if existing_model and cls._is_category_compatible(candidate.canonical_category, existing_model):
                # Verify variant constraints (storage, color) don't conflict
                if not cls._has_variant_conflict(candidate, existing_model):
                    return existing_model, 0.985, f"Exact ModelNumber+Brand match ({model_num_clean})"

        # 4. Match by External Source ID (same source adapter) (Priority 4)
        if candidate.source_id and candidate.external_id:
            existing_offer = db.query(models.MarketplaceOffer).filter(
                models.MarketplaceOffer.marketplace_product_id == candidate.external_id,
                models.MarketplaceOffer.deleted_at.is_(None)
            ).first()
            if existing_offer and existing_offer.master_product_id:
                master = db.get(models.MasterProduct, existing_offer.master_product_id)
                if master and master.is_active and cls._is_category_compatible(candidate.canonical_category, master):
                    return master, 0.98, f"Source external_id match ({candidate.external_id})"

        # 5. Strong Normalized Attribute Ensemble Match (Priority 5)
        # Fetch candidate masters sharing the exact brand
        masters_query = db.query(models.MasterProduct).join(
            models.Brand, models.MasterProduct.brand_id == models.Brand.id
        ).filter(
            models.Brand.name.ilike(candidate.canonical_brand),
            models.MasterProduct.is_active == True
        )
        candidate_masters = masters_query.limit(100).all()

        best_candidate: Optional[models.MasterProduct] = None
        best_confidence = 0.0
        best_reason = ""

        clean_cand_name = cls._simplify_title(candidate.clean_title)

        for master in candidate_masters:
            if not cls._is_category_compatible(candidate.canonical_category, master):
                continue

            # Variant conflict check (e.g., iPhone 18 Pro vs Pro Max, 256GB vs 512GB)
            if cls._has_variant_conflict(candidate, master):
                continue

            master_clean = cls._simplify_title(master.canonical_name)

            # String similarity on canonical product titles
            ratio = SequenceMatcher(None, clean_cand_name, master_clean).ratio()

            # Boost for matching model series
            if candidate.model_series and master.model_series:
                if candidate.model_series.lower() == master.model_series.lower():
                    ratio = min(1.0, ratio + 0.05)

            if ratio > best_confidence:
                best_confidence = ratio
                best_candidate = master
                best_reason = f"Ensemble title/attribute similarity ({ratio:.3f})"

        if best_candidate and best_confidence >= cls.REVIEW_THRESHOLD:
            return best_candidate, round(best_confidence, 3), best_reason

        return None, 0.0, "No duplicate master found"

    @classmethod
    def _is_category_compatible(cls, candidate_category: str, master: models.MasterProduct) -> bool:
        """Enforces hard category compatibility constraint."""
        if not candidate_category or not master.category:
            return True
        master_cat = master.category.name.lower().strip()
        cand_cat = candidate_category.lower().strip()
        return cand_cat == master_cat or cand_cat in master_cat or master_cat in cand_cat

    @classmethod
    def _has_variant_conflict(cls, candidate: NormalizedProductCandidate, master: models.MasterProduct) -> bool:
        """
        Detects if candidate and master have conflicting model variants.
        (e.g., Pro vs Pro Max, Ultra vs standard, 256GB vs 512GB).
        """
        c_name = candidate.clean_title.lower()
        m_name = master.canonical_name.lower()

        # Check 'Pro Max' vs 'Pro' without 'Max'
        if ("pro max" in c_name and "pro max" not in m_name) or ("pro max" in m_name and "pro max" not in c_name):
            return True

        # Check 'Ultra' vs standard
        if ("ultra" in c_name and "ultra" not in m_name) or ("ultra" in m_name and "ultra" not in c_name):
            return True

        # Check 'Plus' vs standard
        if (" plus" in c_name and " plus" not in m_name) or (" plus" in m_name and " plus" not in c_name):
            return True

        # Check storage conflict
        if candidate.storage and master.variant:
            m_variant = master.variant.upper()
            if candidate.storage.upper() in ["128GB", "256GB", "512GB", "1TB"]:
                if candidate.storage.upper() not in m_variant and any(s in m_variant for s in ["128GB", "256GB", "512GB", "1TB"]):
                    return True

        return False

    @classmethod
    def _simplify_title(cls, title: str) -> str:
        """Lowercases and strips common punctuation for similarity matching."""
        if not title:
            return ""
        simplified = re.sub(r"[^\w\s]", " ", title.lower())
        return re.sub(r"\s+", " ", simplified).strip()
