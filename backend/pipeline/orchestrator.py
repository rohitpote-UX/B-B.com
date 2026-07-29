"""
Brand Battle - Pipeline Orchestrator
Connects Queue, Validation, Normalization, AI Matching, Quality Check, Pricing Engine,
Knowledge Graph, DB Ingestion, and Redis Cache.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

from pipeline.validator import DataValidator
from pipeline.normalizer import DataNormalizer
from pipeline.matcher import AIProductMatcher
from pipeline.quality_verifier import QualityVerifier
from pipeline.price_engine import PriceEngine
from pipeline.queue import queue_manager
from pipeline.monitoring import pipeline_monitor
from knowledge_graph.kg_service import kg_service
from redis_client import invalidate_cache_pattern
import models

logger = logging.getLogger("brandbattle.orchestrator")


class PipelineOrchestrator:
    """Master pipeline execution engine processing items from extraction to database ingestion."""

    def __init__(self):
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()
        self.matcher = AIProductMatcher()
        self.verifier = QualityVerifier()
        self.price_engine = PriceEngine()

    def process_raw_item(self, raw_item: Dict[str, Any], db: Session) -> Optional[models.Product]:
        """
        Executes complete pipeline workflow for a single raw scraped item payload:
        Validate -> Normalize -> Quality Check -> KG (Master + Offer) -> Sync to Product -> Price -> Cache Purge
        """
        pipeline_monitor.record_ingest(1)

        # 1. Validation Stage
        is_valid, error_reason, item_valid = self.validator.validate(raw_item)
        if not is_valid:
            pipeline_monitor.record_validation(False)
            queue_manager.push_dlq(raw_item, error_reason)
            logger.warning(f"Validation failed: {error_reason}")
            return None

        pipeline_monitor.record_validation(True)

        # 2. Normalization Stage (standard pipeline normalizer)
        norm_item = self.normalizer.normalize(item_valid)

        # 3. Product Quality Verification (pre-match quality gate)
        passes_quality, quality_score, quality_reason = self.verifier.verify(norm_item, 1.0)
        if not passes_quality:
            pipeline_monitor.record_quality(False)
            queue_manager.push_dlq(norm_item, f"Failed Quality Check: {quality_reason}")
            return None

        pipeline_monitor.record_quality(True)

        # 4. Knowledge Graph Resolution
        #    - Enhanced normalization (KG-specific signals)
        #    - Find or create MasterProduct
        #    - Link MarketplaceOffer
        #    - Sync back to Product table
        try:
            master, is_new, confidence = kg_service.find_or_create_master(norm_item, db)

            if is_new:
                pipeline_monitor.record_match(False)  # Created new master
                pipeline_monitor.record_kg_master_created()
            else:
                pipeline_monitor.record_match(True)  # Matched existing master
                pipeline_monitor.record_kg_master_reused()

            # Link marketplace offer
            offer = kg_service.link_offer(master.id, norm_item, confidence, db)
            pipeline_monitor.record_kg_offer_created()

            # Sync master -> product table (ensures API compatibility)
            product = kg_service.sync_product_from_master(master, db)

        except Exception as e:
            logger.error(f"KG resolution failed, falling back to legacy flow: {e}")
            # Fallback to legacy product creation (ensures pipeline doesn't break)
            product = self._legacy_create_product(norm_item, quality_score, db)
            if not product:
                return None

        # 5. Upsert Marketplace Price Record (legacy Price table)
        platform = norm_item["marketplace"]
        price_val = norm_item["price"]
        orig_price = norm_item.get("original_price") or price_val
        url_val = norm_item.get("product_url", "#")

        price_metrics = self.price_engine.process_price_update(
            product_id=product.id,
            platform=platform,
            price=price_val,
            original_price=orig_price,
            url=url_val
        )

        existing_price = db.query(models.Price).filter(
            models.Price.product_id == product.id,
            models.Price.platform == platform
        ).first()

        if existing_price:
            existing_price.price = price_val
            existing_price.original_price = orig_price
            existing_price.discount_percentage = price_metrics["discount_percentage"]
            existing_price.url = url_val
            existing_price.is_available = True
        else:
            new_price = models.Price(
                product_id=product.id,
                platform=platform,
                price=price_val,
                original_price=orig_price,
                discount_percentage=price_metrics["discount_percentage"],
                url=url_val,
                seller_name=norm_item.get("seller_name"),
                is_available=True
            )
            db.add(new_price)

        # 6. Log Timestamped Price History Snapshot
        history_entry = models.PriceHistory(
            product_id=product.id,
            platform=platform,
            price=price_val,
            currency=norm_item.get("currency", "INR")
        )
        db.add(history_entry)

        # 7. Re-evaluate Product Best Price & Deal Score
        all_prices = db.query(models.Price).filter(
            models.Price.product_id == product.id,
            models.Price.is_available == True
        ).all()

        if all_prices:
            lowest = min(p.price for p in all_prices)
            highest = max(p.price for p in all_prices)
            best_p = next(p for p in all_prices if p.price == lowest)

            product.current_best_price = lowest
            product.lowest_price = lowest
            product.highest_price = highest
            product.current_best_platform = best_p.platform
            product.deal_score = max(product.deal_score or 50.0, price_metrics["deal_score"])

        db.commit()
        db.refresh(product)

        # 8. Redis Cache Invalidation
        invalidate_cache_pattern("product:*")
        invalidate_cache_pattern("deals:*")
        pipeline_monitor.record_cache_purge()

        logger.info(f"✅ Pipeline processed '{product.name}' [ID: {product.id}] via {platform}")
        return product

    def _legacy_create_product(
        self, norm_item: Dict[str, Any], quality_score: float, db: Session
    ) -> Optional[models.Product]:
        """Fallback product creation when KG resolution fails. Preserves original pipeline behavior."""
        brand_name = norm_item["canonical_brand"]
        brand_obj = db.query(models.Brand).filter(models.Brand.name.ilike(brand_name)).first()
        if not brand_obj:
            brand_slug = brand_name.lower().replace(" ", "-")
            brand_obj = models.Brand(name=brand_name, slug=brand_slug, trust_score=8.5)
            db.add(brand_obj)
            db.flush()

        cat_name = norm_item["canonical_category"]
        cat_obj = db.query(models.Category).filter(models.Category.name.ilike(cat_name)).first()
        if not cat_obj:
            cat_slug = cat_name.lower().replace(" ", "-")
            cat_obj = models.Category(name=cat_name, slug=cat_slug)
            db.add(cat_obj)
            db.flush()

        # Check if product already exists
        existing = db.query(models.Product).filter(
            models.Product.slug == norm_item["suggested_slug"]
        ).first()
        if existing:
            if norm_item["normalized_specs"]:
                specs = existing.specifications or {}
                specs.update(norm_item["normalized_specs"])
                existing.specifications = specs
            return existing

        base_slug = norm_item["suggested_slug"]
        slug = base_slug
        counter = 1
        while db.query(models.Product).filter(models.Product.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = models.Product(
            name=norm_item["clean_title"],
            slug=slug,
            brand_id=brand_obj.id,
            category_id=cat_obj.id,
            description=f"High performance {cat_name} by {brand_name}.",
            image_url=norm_item.get("image_url"),
            specifications=norm_item["normalized_specs"],
            average_rating=norm_item.get("rating") or 4.5,
            total_reviews=norm_item.get("total_reviews") or 100,
            current_best_price=norm_item["price"],
            current_best_platform=norm_item["marketplace"],
            deal_score=quality_score,
            is_active=True
        )
        db.add(product)
        db.flush()
        return product

    def run_pipeline_batch(self, raw_items: List[Dict[str, Any]], db: Session) -> Dict[str, Any]:
        """Runs batch of items through pipeline with isolated error recovery."""
        processed = 0
        failed = 0
        for item in raw_items:
            try:
                res = self.process_raw_item(item, db)
                if res:
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                db.rollback()
                failed += 1
                logger.error(f"Error processing pipeline item: {e}")

        return {"processed": processed, "failed": failed, "batch_total": len(raw_items)}


# Global orchestrator instance
pipeline_orchestrator = PipelineOrchestrator()
