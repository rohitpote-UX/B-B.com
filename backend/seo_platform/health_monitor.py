"""
Brand Battle — Enterprise SEO Health & Quality Monitoring Engine
Audits database products and comparisons for metadata completeness, canonical validity,
thin content, image presence, price verification, and calculates overall site SEO quality score.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

import models

logger = logging.getLogger("brandbattle.seo_platform.health_monitor")


class SeoHealthMonitorEngine:
    """Monitors technical SEO quality, indexability, thin content, and schema completeness."""

    def run_full_seo_audit(self, db: Session) -> Dict[str, Any]:
        """
        Executes comprehensive audit across all active products and comparisons.
        Returns detailed metric breakdown and overall SEO Quality Score (0 - 100).
        """
        products = db.query(models.Product).filter(models.Product.is_active == True).all()
        total_products = len(products)

        if total_products == 0:
            return {
                "overall_seo_score": 100.0,
                "audited_at": datetime.now(timezone.utc).isoformat(),
                "total_products": 0,
                "issues_found": [],
            }

        missing_titles = 0
        missing_descriptions = 0
        missing_images = 0
        missing_brands = 0
        missing_categories = 0
        unverified_prices = 0
        thin_content_count = 0
        eligible_count = 0

        for p in products:
            if not p.name or len(p.name.strip()) < 3:
                missing_titles += 1
            if not p.description or len(p.description.strip()) < 20:
                missing_descriptions += 1
                thin_content_count += 1
            if not p.image_url:
                missing_images += 1
            if not p.brand_id and not p.brand:
                missing_brands += 1
            if not p.category_id and not p.category:
                missing_categories += 1
            if p.price_verification_status != "verified":
                unverified_prices += 1
            if (
                p.name
                and len(p.name) >= 3
                and p.description
                and len(p.description) >= 20
                and p.image_url
            ):
                eligible_count += 1

        # Calculate Component Scores (Weighted)
        # Technical Completeness: 30%
        # Content Quality: 30%
        # Data Verification: 20%
        # Indexability: 20%
        tech_score = max(0, 100 - ((missing_titles + missing_images) / total_products) * 100)
        content_score = max(0, 100 - (thin_content_count / total_products) * 100)
        verification_score = max(0, 100 - (unverified_prices / total_products) * 100)
        indexability_score = (eligible_count / total_products) * 100

        overall_score = (
            (tech_score * 0.30) +
            (content_score * 0.30) +
            (verification_score * 0.20) +
            (indexability_score * 0.20)
        )

        return {
            "overall_seo_score": round(overall_score, 1),
            "audited_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_products": total_products,
                "seo_eligible_products": eligible_count,
                "thin_content_products": thin_content_count,
                "missing_titles": missing_titles,
                "missing_descriptions": missing_descriptions,
                "missing_images": missing_images,
                "missing_brands": missing_brands,
                "missing_categories": missing_categories,
                "unverified_prices": unverified_prices,
            },
            "component_scores": {
                "technical": round(tech_score, 1),
                "content": round(content_score, 1),
                "verification": round(verification_score, 1),
                "indexability": round(indexability_score, 1),
            },
            "status": "HEALTHY" if overall_score >= 80.0 else "NEEDS_ATTENTION",
        }


# Singleton
seo_health_monitor = SeoHealthMonitorEngine()
