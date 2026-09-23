"""
Brand Battle — Product Quality Scorer & Publishing Gate
Calculates internal completeness and data integrity scores (0-100)
and gates unverified/incomplete products from publishing.
"""

from typing import Tuple, List, Dict, Any
from catalog_engine.schemas import NormalizedProductCandidate


class ProductQualityScorer:
    """
    Computes deterministic quality scores based on presence, completeness,
    and format validity of canonical identity attributes.
    """

    PUBLISHING_THRESHOLD = 70.0

    @classmethod
    def evaluate(cls, candidate: NormalizedProductCandidate) -> Tuple[float, bool, List[str]]:
        """
        Evaluates a candidate.
        Returns: (quality_score: float, is_publishable: bool, audit_reasons: List[str])
        """
        score = 0.0
        reasons: List[str] = []

        # 1. Canonical Brand (15 pts)
        if candidate.canonical_brand and candidate.canonical_brand.lower() != "generic":
            score += 15.0
            reasons.append("Valid canonical brand (+15)")
        else:
            reasons.append("Missing or generic brand (0/15)")

        # 2. Canonical Product/Model Name (20 pts)
        name = candidate.canonical_name or candidate.clean_title
        if name and len(name.strip()) >= 3:
            score += 20.0
            reasons.append("Valid canonical name (+20)")
        else:
            reasons.append("Missing or too short product name (0/20)")

        # 3. Canonical Category (15 pts)
        if candidate.canonical_category and candidate.canonical_category != "Uncategorized":
            score += 15.0
            reasons.append("Canonical category resolved (+15)")
        else:
            reasons.append("Uncategorized product (0/15)")

        # 4. Valid GTIN / EAN / UPC or MPN (15 pts)
        if candidate.is_gtin_valid and (candidate.gtin or candidate.ean or candidate.upc):
            score += 15.0
            reasons.append("Validated GS1 GTIN/EAN/UPC identifier (+15)")
        elif candidate.mpn and len(candidate.mpn.strip()) >= 4:
            score += 12.0
            reasons.append("Verified MPN present (+12)")
        elif candidate.model_number and len(candidate.model_number.strip()) >= 3:
            score += 8.0
            reasons.append("Model number present (+8)")
        else:
            reasons.append("No authoritative manufacturer identifiers (0/15)")

        # 5. Structured Specifications (15 pts)
        specs_count = len(candidate.specifications) if candidate.specifications else 0
        if specs_count >= 5:
            score += 15.0
            reasons.append(f"Rich specifications ({specs_count} attributes) (+15)")
        elif specs_count >= 2:
            score += 8.0
            reasons.append(f"Basic specifications ({specs_count} attributes) (+8)")
        else:
            reasons.append("Missing or insufficient specifications (0/15)")

        # 6. Valid Primary Image (10 pts)
        if candidate.primary_image_url and candidate.primary_image_url.startswith("http"):
            score += 10.0
            reasons.append("Primary image present (+10)")
        else:
            reasons.append("Missing primary image (0/10)")

        # 7. Clean Description (10 pts)
        if candidate.description and len(candidate.description.strip()) >= 15:
            score += 10.0
            reasons.append("Detailed description (+10)")
        elif candidate.description and len(candidate.description.strip()) >= 5:
            score += 5.0
            reasons.append("Short description (+5)")
        else:
            reasons.append("Missing description (0/10)")

        # 8. Provenance Metadata (5 pts)
        if candidate.source_id and candidate.external_id:
            score += 5.0
            reasons.append("Verified source provenance logged (+5)")

        score = min(100.0, round(score, 1))

        # Publishing rule: score >= 70 AND has brand, name, and category
        has_min_identity = bool(
            candidate.canonical_brand
            and candidate.canonical_name
            and len(candidate.canonical_name) >= 3
            and candidate.canonical_category
        )
        is_publishable = (score >= cls.PUBLISHING_THRESHOLD) and has_min_identity

        return score, is_publishable, reasons
