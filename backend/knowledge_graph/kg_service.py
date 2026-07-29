"""
Brand Battle - Knowledge Graph Service
Core service layer for the Product Knowledge Graph. Manages MasterProduct lifecycle,
marketplace offer linking, graph metrics, and Product table synchronization.
"""

import re
import uuid as uuid_lib
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import logging

import models
from knowledge_graph.normalizer_enhanced import EnhancedNormalizer
from knowledge_graph.matcher_enhanced import EnhancedMatcher
from knowledge_graph.relationship_engine import RelationshipEngine
from knowledge_graph.cache_manager import KGCacheManager
from knowledge_graph.event_bus import event_bus
from knowledge_graph.completeness import completeness_calculator
from knowledge_graph.observability import log_audit_event, trace_kg_operation, get_correlation_id
from knowledge_graph.versioning import version_manager
from knowledge_graph.review_queue import review_queue_engine

logger = logging.getLogger("brandbattle.kg.service")


class KnowledgeGraphService:
    """
    Central domain service orchestrating all Knowledge Graph operations.
    Acts as the single source of truth and domain interface for product resolution,
    versioning, audit logging, and relationship management.
    """

    def __init__(self):
        self.normalizer = EnhancedNormalizer()
        self.matcher = EnhancedMatcher()
        self.relationship_engine = RelationshipEngine()
        self.cache = KGCacheManager()
        self.event_bus = event_bus
        self.version_manager = version_manager
        self.completeness_calculator = completeness_calculator
        self.review_queue = review_queue_engine

    # ─── Master Product Resolution ───────────────────────────────────

    def find_or_create_master(
        self,
        normalized_item: Dict[str, Any],
        db: Session,
    ) -> Tuple[models.MasterProduct, bool, float]:
        """
        Core KG operation: finds an existing MasterProduct or creates a new one.

        Returns: (master_product, is_new, confidence_score)
        """
        # 1. Enhance the normalized item with KG-specific signals
        enhanced = self.normalizer.enhance_normalized_item(normalized_item)

        # 2. Build candidate list from existing masters
        candidates = self._get_master_candidates(enhanced, db)

        # 3. Match against candidates via Hybrid AI Matcher
        matched, confidence = self.matcher.match_to_master(enhanced, candidates, db=db)

        if matched:
            # Found existing master — update it with richer data
            master = matched["db_obj"]
            self._enrich_master(master, enhanced, confidence, db)

            # Record Matching Confidence History
            conf_hist = models.MatchingConfidenceHistory(
                master_product_id=master.id,
                matching_score=confidence,
                algorithm_version="v2.0_multi_signal",
                model_version="gemini-flash-kg",
                decision_type="auto_matched",
                matching_signals={
                    "title": enhanced.get("clean_title"),
                    "brand": enhanced.get("canonical_brand"),
                    "matched_master_id": master.id,
                }
            )
            db.add(conf_hist)

            # Route to review queue if confidence is borderline (0.50 < confidence < 0.72)
            if 0.50 < confidence < 0.72:
                self.review_queue.queue_for_review(
                    trigger_reason="borderline_match_confidence",
                    confidence_score=confidence,
                    payload={"item_title": enhanced.get("clean_title"), "master_title": master.canonical_name},
                    master_id=master.id,
                    priority="low",
                    db=db
                )

            return master, False, confidence
        else:
            # Create new master
            master = self._create_master(enhanced, db)

            # Record Matching Confidence History
            conf_hist = models.MatchingConfidenceHistory(
                master_product_id=master.id,
                matching_score=confidence,
                algorithm_version="v2.0_multi_signal",
                model_version="gemini-flash-kg",
                decision_type="auto_created",
                matching_signals={"title": enhanced.get("clean_title")}
            )
            db.add(conf_hist)

            return master, True, confidence

    def _get_master_candidates(self, item: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Fetch candidate MasterProducts for matching, filtered by brand if known."""
        brand = item.get("canonical_brand", "")
        category = item.get("canonical_category", "")

        q = db.query(models.MasterProduct).filter(models.MasterProduct.is_active == True)

        # Pre-filter by brand if known (brand_id lookup)
        if brand:
            brand_obj = db.query(models.Brand).filter(models.Brand.name.ilike(brand)).first()
            if brand_obj:
                q = q.filter(models.MasterProduct.brand_id == brand_obj.id)

        masters = q.limit(200).all()

        return [
            {
                "id": m.id,
                "canonical_name": m.canonical_name,
                "brand_name": m.brand.name if m.brand else "",
                "category_name": m.category.name if m.category else "",
                "specifications": m.specifications or {},
                "color_family": m.color_family,
                "material": m.material,
                "gender": m.gender,
                "product_type": m.product_type,
                "model_series": m.model_series,
                "model_name": m.model_name,
                "db_obj": m,
            }
            for m in masters
        ]

    def _create_master(self, item: Dict[str, Any], db: Session) -> models.MasterProduct:
        """Creates a new MasterProduct from a normalized item."""
        title = item.get("clean_title", item.get("raw_title", ""))
        brand_name = item.get("canonical_brand", "")
        category_name = item.get("canonical_category", "")

        # Resolve brand
        brand_obj = None
        if brand_name:
            brand_obj = db.query(models.Brand).filter(models.Brand.name.ilike(brand_name)).first()
            if not brand_obj:
                brand_slug = brand_name.lower().replace(" ", "-")
                brand_obj = models.Brand(name=brand_name, slug=brand_slug, trust_score=7.0)
                db.add(brand_obj)
                db.flush()

        # Resolve category
        cat_obj = None
        parent_cat = item.get("kg_parent_category", category_name)
        if parent_cat:
            cat_obj = db.query(models.Category).filter(models.Category.name.ilike(parent_cat)).first()
            if not cat_obj:
                cat_slug = parent_cat.lower().replace(" ", "-")
                cat_obj = models.Category(name=parent_cat, slug=cat_slug)
                db.add(cat_obj)
                db.flush()

        # Resolve subcategory
        subcat_obj = None
        subcategory = item.get("kg_subcategory")
        if subcategory:
            subcat_obj = db.query(models.Category).filter(models.Category.name.ilike(subcategory)).first()
            if not subcat_obj and cat_obj:
                subcat_slug = subcategory.lower().replace(" ", "-")
                subcat_obj = models.Category(name=subcategory, slug=subcat_slug)
                db.add(subcat_obj)
                db.flush()

        # Generate unique slug
        base_slug = item.get("suggested_slug", re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-'))
        slug = base_slug
        counter = 1
        while db.query(models.MasterProduct).filter(models.MasterProduct.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        price = item.get("price")
        rating = item.get("rating")
        reviews = item.get("total_reviews")

        master = models.MasterProduct(
            uuid=str(uuid_lib.uuid4()),
            canonical_name=title,
            slug=slug,
            brand_id=brand_obj.id if brand_obj else None,
            category_id=cat_obj.id if cat_obj else None,
            subcategory_id=subcat_obj.id if subcat_obj else None,
            description=item.get("description", f"High quality {category_name} by {brand_name}."),
            gender=item.get("kg_gender"),
            color_family=item.get("kg_color_family"),
            material=item.get("kg_material"),
            product_type=item.get("kg_product_type"),
            model_series=item.get("kg_model_series"),
            model_name=item.get("kg_model_name"),
            variant=item.get("kg_variant"),
            specifications=item.get("normalized_specs", {}),
            features=item.get("features"),
            primary_image_url=item.get("image_url"),
            images=[item.get("image_url")] if item.get("image_url") else [],
            offer_count=1,
            lowest_price=price,
            highest_price=price,
            average_rating=rating or 0.0,
            total_reviews=reviews or 0,
            confidence_score=1.0,  # New master, self-referential confidence
            version=1,
            status=models.ProductLifecycleState.ACTIVE.value,
            is_active=True,
        )
        db.add(master)
        db.flush()

        # Set stable human-readable public ID (BB-PRD-0000000001)
        master.public_id = f"BB-PRD-{master.id:010d}"

        # Create structured attributes
        self._create_attributes(master.id, item, db)

        # Create product image record
        if item.get("image_url"):
            img = models.ProductImage(
                master_product_id=master.id,
                url=item["image_url"],
                source_marketplace=item.get("marketplace"),
                alt_text=title,
                is_primary=True,
                sort_order=0,
            )
            db.add(img)

        # Create tags
        self._create_tags(master.id, item, db)

        # Create search metadata
        search_vector = self._build_search_vector(item)
        sm = models.SearchMetadata(
            master_product_id=master.id,
            search_vector=search_vector,
            synonyms=self._generate_synonyms(item),
            boost_score=1.0,
            trending_score=0.0,
        )
        db.add(sm)

        # Calculate completeness score
        self.completeness_calculator.calculate_score(master, db)

        # Create initial Version 1 snapshot
        self.version_manager.create_version_snapshot(
            master=master,
            changed_fields=["initial_creation"],
            source_of_change="system",
            updated_by="pipeline",
            change_reason="Initial MasterProduct creation",
            db=db
        )

        # Audit Event Logging
        log_audit_event(
            db=db,
            entity_type="master_product",
            entity_id=master.id,
            action=models.AuditEventType.MASTER_CREATED.value,
            new_value={"canonical_name": master.canonical_name, "public_id": master.public_id},
            reason="MasterProduct created by ingestion pipeline",
            actor="pipeline"
        )

        # Domain Event Publishing
        self.event_bus.publish(
            event_type="MasterProductCreated",
            entity_id=master.id,
            payload={"public_id": master.public_id, "canonical_name": master.canonical_name, "slug": master.slug},
            actor="pipeline"
        )

        logger.info(f"Created new MasterProduct: '{title}' [ID: {master.id}, PublicID: {master.public_id}]")
        return master

    def _enrich_master(
        self,
        master: models.MasterProduct,
        item: Dict[str, Any],
        confidence: float,
        db: Session,
    ) -> None:
        """Enrich an existing MasterProduct with data from a new offer."""
        changed_fields = []

        # Merge specifications (additive)
        if item.get("normalized_specs"):
            existing_specs = master.specifications or {}
            new_specs = item["normalized_specs"]
            for key, val in new_specs.items():
                if key not in existing_specs:
                    existing_specs[key] = val
                    changed_fields.append(f"spec:{key}")
            master.specifications = existing_specs

        # Add image if new
        img_url = item.get("image_url")
        if img_url:
            existing_images = master.images or []
            if img_url not in existing_images:
                existing_images.append(img_url)
                master.images = existing_images
                changed_fields.append("images")

        # Fill in missing identity fields
        if not master.gender and item.get("kg_gender"):
            master.gender = item["kg_gender"]
            changed_fields.append("gender")
        if not master.color_family and item.get("kg_color_family"):
            master.color_family = item["kg_color_family"]
            changed_fields.append("color_family")
        if not master.material and item.get("kg_material"):
            master.material = item["kg_material"]
            changed_fields.append("material")
        if not master.product_type and item.get("kg_product_type"):
            master.product_type = item["kg_product_type"]
            changed_fields.append("product_type")
        if not master.model_series and item.get("kg_model_series"):
            master.model_series = item["kg_model_series"]
            changed_fields.append("model_series")
        if not master.model_name and item.get("kg_model_name"):
            master.model_name = item["kg_model_name"]
            changed_fields.append("model_name")

        # Update confidence (running average)
        master.confidence_score = (master.confidence_score + confidence) / 2

        # Increment offer count
        master.offer_count = (master.offer_count or 0) + 1

        # Ensure public_id exists
        if not master.public_id:
            master.public_id = f"BB-PRD-{master.id:010d}"

        # Recalculate completeness score
        self.completeness_calculator.calculate_score(master, db)

        # Snapshot version if significant fields changed
        if changed_fields:
            self.version_manager.create_version_snapshot(
                master=master,
                changed_fields=changed_fields,
                source_of_change="enrichment",
                updated_by="pipeline",
                change_reason=f"Enriched with offer data ({len(changed_fields)} fields modified)",
                db=db
            )

            # Audit Event Logging
            log_audit_event(
                db=db,
                entity_type="master_product",
                entity_id=master.id,
                action=models.AuditEventType.MASTER_UPDATED.value,
                new_value={"changed_fields": changed_fields},
                reason=f"Enriched with offer data ({', '.join(changed_fields[:5])})",
                actor="pipeline"
            )

            # Domain Event Publishing
            self.event_bus.publish(
                event_type="MasterProductUpdated",
                entity_id=master.id,
                payload={"public_id": master.public_id, "changed_fields": changed_fields},
                actor="pipeline"
            )
        master.confidence_score = (master.confidence_score + confidence) / 2

        # Increment offer count
        master.offer_count = (master.offer_count or 0) + 1

    # ─── Marketplace Offer Management ────────────────────────────────

    def link_offer(
        self,
        master_id: int,
        item: Dict[str, Any],
        confidence: float,
        db: Session,
    ) -> models.MarketplaceOffer:
        """Creates or updates a MarketplaceOffer linked to a MasterProduct."""
        marketplace = item.get("marketplace", "")
        url = item.get("product_url", "#")

        # Check if offer already exists for this marketplace + URL
        existing = (
            db.query(models.MarketplaceOffer)
            .filter(
                models.MarketplaceOffer.master_product_id == master_id,
                models.MarketplaceOffer.marketplace == marketplace,
                models.MarketplaceOffer.url == url,
            )
            .first()
        )

        price = item.get("price", 0)
        orig_price = item.get("original_price")
        discount_pct = 0.0
        if orig_price and orig_price > price:
            discount_pct = round(((orig_price - price) / orig_price) * 100, 1)

        if existing:
            # Update existing offer
            existing.price = price
            existing.original_price = orig_price
            existing.discount_percentage = discount_pct
            existing.title = item.get("clean_title", item.get("raw_title", ""))
            existing.image_url = item.get("image_url")
            existing.seller_name = item.get("seller_name")
            existing.rating = item.get("rating")
            existing.review_count = item.get("total_reviews", 0)
            existing.match_confidence = confidence
            existing.is_available = item.get("availability", True)
            existing.last_scraped = datetime.now(timezone.utc)
            existing.status = models.OfferStatus.ACTIVE.value
            return existing

        # Create new offer
        offer = models.MarketplaceOffer(
            master_product_id=master_id,
            marketplace=marketplace,
            title=item.get("clean_title", item.get("raw_title", "")),
            url=url,
            image_url=item.get("image_url"),
            price=price,
            original_price=orig_price,
            discount_percentage=discount_pct,
            currency=item.get("currency", "INR"),
            seller_name=item.get("seller_name"),
            seller_rating=None,
            review_count=item.get("total_reviews", 0),
            rating=item.get("rating"),
            is_available=item.get("availability", True),
            match_confidence=confidence,
            last_scraped=datetime.now(timezone.utc),
        )
        db.add(offer)
        db.flush()
        return offer

    # ─── Product Table Synchronization ───────────────────────────────

    def sync_product_from_master(self, master: models.MasterProduct, db: Session) -> models.Product:
        """
        Ensures the legacy Product table stays in sync with the MasterProduct.
        Finds or creates a Product record linked to the given master.
        Updates best price, platform, ratings from the master's offers.
        """
        # Find existing linked product
        product = (
            db.query(models.Product)
            .filter(models.Product.master_product_id == master.id)
            .first()
        )

        if not product:
            # Also try by slug match
            product = db.query(models.Product).filter(models.Product.slug == master.slug).first()
            if product:
                product.master_product_id = master.id

        if not product:
            # Create new Product record
            product = models.Product(
                name=master.canonical_name,
                slug=master.slug,
                brand_id=master.brand_id,
                category_id=master.category_id,
                description=master.description,
                image_url=master.primary_image_url,
                images=master.images,
                specifications=master.specifications,
                features=master.features,
                average_rating=master.average_rating,
                total_reviews=master.total_reviews,
                lowest_price=master.lowest_price,
                highest_price=master.highest_price,
                current_best_price=master.lowest_price,
                ai_summary=master.ai_summary,
                is_active=True,
                master_product_id=master.id,
            )
            db.add(product)
            db.flush()
        else:
            # Sync fields from master
            product.name = master.canonical_name
            product.brand_id = master.brand_id
            product.category_id = master.category_id
            if master.description:
                product.description = master.description
            if master.primary_image_url:
                product.image_url = master.primary_image_url
            if master.images:
                product.images = master.images
            if master.specifications:
                product.specifications = master.specifications
            if master.features:
                product.features = master.features

        # Recompute best price from all offers
        offers = (
            db.query(models.MarketplaceOffer)
            .filter(
                models.MarketplaceOffer.master_product_id == master.id,
                models.MarketplaceOffer.is_available == True,
            )
            .all()
        )

        if offers:
            prices = [o.price for o in offers]
            best_offer = min(offers, key=lambda o: o.price)
            product.lowest_price = min(prices)
            product.highest_price = max(prices)
            product.current_best_price = best_offer.price
            product.current_best_platform = best_offer.marketplace

            # Update master metrics too
            master.lowest_price = product.lowest_price
            master.highest_price = product.highest_price

            # Aggregate ratings from offers
            rated_offers = [o for o in offers if o.rating]
            if rated_offers:
                avg_rating = sum(o.rating for o in rated_offers) / len(rated_offers)
                total_reviews = sum(o.review_count for o in rated_offers)
                product.average_rating = round(avg_rating, 1)
                product.total_reviews = total_reviews
                master.average_rating = product.average_rating
                master.total_reviews = product.total_reviews

        # Invalidate caches
        self.cache.invalidate_master(master.id)

        return product

    # ─── Graph Metrics ───────────────────────────────────────────────

    def compute_graph_metrics(self, db: Session) -> Dict[str, Any]:
        """Compute and store overall Knowledge Graph health metrics."""
        total_masters = db.query(func.count(models.MasterProduct.id)).filter(
            models.MasterProduct.is_active == True
        ).scalar() or 0

        total_offers = db.query(func.count(models.MarketplaceOffer.id)).scalar() or 0

        total_relationships = db.query(func.count(models.ProductRelationship.id)).scalar() or 0

        total_attributes = db.query(func.count(models.ProductAttribute.id)).scalar() or 0

        orphan_products = db.query(func.count(models.Product.id)).filter(
            models.Product.master_product_id == None,
            models.Product.is_active == True,
        ).scalar() or 0

        avg_confidence = db.query(func.avg(models.MasterProduct.confidence_score)).scalar() or 0.0

        avg_offers = total_offers / max(total_masters, 1)

        # Duplicate detection rate: masters with offer_count > 1
        multi_offer_masters = db.query(func.count(models.MasterProduct.id)).filter(
            models.MasterProduct.offer_count > 1,
            models.MasterProduct.is_active == True,
        ).scalar() or 0
        dup_rate = multi_offer_masters / max(total_masters, 1)

        metrics = {
            "total_masters": total_masters,
            "total_offers": total_offers,
            "total_relationships": total_relationships,
            "total_attributes": total_attributes,
            "orphan_products": orphan_products,
            "avg_confidence": round(avg_confidence, 3),
            "avg_offers_per_master": round(avg_offers, 2),
            "duplicate_detection_rate": round(dup_rate, 3),
        }

        # Upsert GraphMetrics singleton
        gm = db.query(models.GraphMetrics).first()
        if gm:
            gm.total_masters = total_masters
            gm.total_offers = total_offers
            gm.total_relationships = total_relationships
            gm.total_attributes = total_attributes
            gm.orphan_products = orphan_products
            gm.avg_confidence = round(avg_confidence, 3)
            gm.avg_offers_per_master = round(avg_offers, 2)
            gm.duplicate_detection_rate = round(dup_rate, 3)
            gm.last_computed = datetime.now(timezone.utc)
        else:
            gm = models.GraphMetrics(**metrics)
            db.add(gm)

        db.flush()

        self.cache.set_stats(metrics)
        return metrics

    # ─── Master Merge ────────────────────────────────────────────────

    def merge_masters(self, source_id: int, target_id: int, db: Session) -> bool:
        """
        Merge source MasterProduct into target. Moves all offers, relationships,
        and linked products to the target, then deactivates the source.
        """
        source = db.query(models.MasterProduct).filter(models.MasterProduct.id == source_id).first()
        target = db.query(models.MasterProduct).filter(models.MasterProduct.id == target_id).first()
        if not source or not target:
            return False

        # Move offers
        for offer in source.offers:
            offer.master_product_id = target_id

        # Move linked products
        for product in source.products:
            product.master_product_id = target_id

        # Move attributes (skip duplicates)
        for attr in source.attributes:
            existing = (
                db.query(models.ProductAttribute)
                .filter(
                    models.ProductAttribute.master_product_id == target_id,
                    models.ProductAttribute.attribute_name == attr.attribute_name,
                )
                .first()
            )
            if not existing:
                attr.master_product_id = target_id

        # Move images
        for img in source.kg_images:
            img.master_product_id = target_id

        # Move tags (skip duplicates)
        for tag in source.tags:
            existing = (
                db.query(models.ProductTag)
                .filter(
                    models.ProductTag.master_product_id == target_id,
                    models.ProductTag.tag == tag.tag,
                )
                .first()
            )
            if not existing:
                tag.master_product_id = target_id

        # Merge specifications
        if source.specifications:
            target_specs = target.specifications or {}
            for key, val in source.specifications.items():
                if key not in target_specs:
                    target_specs[key] = val
            target.specifications = target_specs

        # Merge images list
        source_imgs = source.images or []
        target_imgs = target.images or []
        for img in source_imgs:
            if img not in target_imgs:
                target_imgs.append(img)
        target.images = target_imgs

        # Update offer count
        target.offer_count = (target.offer_count or 0) + (source.offer_count or 0)

        # Deactivate source
        source.is_active = False

        db.flush()

        # Re-sync the target product
        self.sync_product_from_master(target, db)

        # Invalidate caches
        self.cache.invalidate_master(source_id)
        self.cache.invalidate_master(target_id)

        logger.info(f"Merged Master {source_id} into Master {target_id}")
        return True

    # ─── Helpers ─────────────────────────────────────────────────────

    def _create_attributes(self, master_id: int, item: Dict[str, Any], db: Session) -> None:
        """Create structured ProductAttribute records from specs."""
        specs = item.get("normalized_specs", item.get("specifications", {}))
        if not specs:
            return

        for key, val in specs.items():
            # Determine attribute type
            attr_type = models.AttributeType.TEXT.value
            unit = None
            val_str = str(val)

            if isinstance(val, bool):
                attr_type = models.AttributeType.BOOLEAN.value
            elif isinstance(val, (int, float)):
                attr_type = models.AttributeType.NUMERIC.value
            elif re.match(r'^\d+\s*(GB|TB|MB|MHz|GHz|mAh|mm|cm|kg|g|W|V)$', val_str, re.IGNORECASE):
                attr_type = models.AttributeType.NUMERIC.value
                unit_match = re.search(r'(GB|TB|MB|MHz|GHz|mAh|mm|cm|kg|g|W|V)$', val_str, re.IGNORECASE)
                if unit_match:
                    unit = unit_match.group(1)

            attr = models.ProductAttribute(
                master_product_id=master_id,
                attribute_name=key.strip(),
                attribute_value=val_str,
                attribute_type=attr_type,
                unit=unit,
                is_searchable=True,
            )
            db.add(attr)

    def _create_tags(self, master_id: int, item: Dict[str, Any], db: Session) -> None:
        """Create ProductTag records from item metadata."""
        tags_added = set()

        # From explicit tags
        for tag in (item.get("tags") or []):
            tag_clean = str(tag).strip().lower()
            if tag_clean and tag_clean not in tags_added:
                db.add(models.ProductTag(master_product_id=master_id, tag=tag_clean, tag_type="general"))
                tags_added.add(tag_clean)

        # From KG fields
        for field, tag_type in [
            ("canonical_brand", "brand"),
            ("canonical_category", "category"),
            ("kg_product_type", "product_type"),
            ("kg_gender", "gender"),
            ("kg_color_family", "color"),
            ("kg_material", "material"),
            ("kg_model_series", "model_series"),
        ]:
            val = item.get(field)
            if val:
                val_clean = str(val).strip().lower()
                if val_clean and val_clean not in tags_added:
                    db.add(models.ProductTag(master_product_id=master_id, tag=val_clean, tag_type=tag_type))
                    tags_added.add(val_clean)

    def _build_search_vector(self, item: Dict[str, Any]) -> str:
        """Build a concatenated searchable text string."""
        parts = [
            item.get("clean_title", ""),
            item.get("canonical_brand", ""),
            item.get("canonical_category", ""),
            item.get("kg_product_type", ""),
            item.get("kg_model_series", ""),
            item.get("kg_model_name", ""),
            item.get("kg_color_family", ""),
            item.get("kg_material", ""),
            item.get("kg_gender", ""),
        ]
        # Add specification values
        specs = item.get("normalized_specs", {})
        parts.extend(str(v) for v in specs.values())

        # Add tags
        for tag in (item.get("tags") or []):
            parts.append(str(tag))

        return " ".join(filter(None, parts)).lower()

    def _generate_synonyms(self, item: Dict[str, Any]) -> List[str]:
        """Generate search synonyms for a product."""
        synonyms = []
        product_type = item.get("kg_product_type", "")

        type_synonyms = {
            "sneakers": ["trainers", "kicks", "athletic shoes"],
            "smartphone": ["mobile", "phone", "cellphone", "handset"],
            "laptop": ["notebook", "portable computer"],
            "headphones": ["cans", "earphones", "audio"],
            "tshirt": ["tee", "t-shirt", "t shirt"],
            "watch": ["timepiece", "wristwatch"],
            "smartwatch": ["smart watch", "fitness watch", "wearable"],
            "jeans": ["denim", "denim pants"],
        }

        if product_type in type_synonyms:
            synonyms.extend(type_synonyms[product_type])

        return synonyms

    # ─── Soft Delete & Lifecycle Operations ─────────────────────────

    def soft_delete_master(
        self, master_id: int, reason: str = "Admin deletion", actor: str = "admin", db: Session = None
    ) -> bool:
        """Soft deletes a MasterProduct by marking status=deleted and setting deleted_at timestamp."""
        master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
        if not master:
            return False

        prev_status = master.status
        master.status = models.ProductLifecycleState.DELETED.value
        master.is_active = False
        master.deleted_at = datetime.now(timezone.utc)

        log_audit_event(
            db=db,
            entity_type="master_product",
            entity_id=master_id,
            action="soft_delete",
            previous_value={"status": prev_status, "is_active": True},
            new_value={"status": master.status, "is_active": False},
            reason=reason,
            actor=actor
        )

        self.event_bus.publish("ProductArchived", master_id, {"reason": reason}, actor=actor)
        self.cache.invalidate_master(master_id)
        return True

    def restore_master(self, master_id: int, actor: str = "admin", db: Session = None) -> bool:
        """Restores a soft-deleted MasterProduct to active state."""
        master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
        if not master:
            return False

        prev_status = master.status
        master.status = models.ProductLifecycleState.ACTIVE.value
        master.is_active = True
        master.deleted_at = None

        log_audit_event(
            db=db,
            entity_type="master_product",
            entity_id=master_id,
            action="restore",
            previous_value={"status": prev_status},
            new_value={"status": master.status},
            reason="MasterProduct restored from soft delete",
            actor=actor
        )

        self.cache.invalidate_master(master_id)
        return True


# Global singleton instance
kg_service = KnowledgeGraphService()
