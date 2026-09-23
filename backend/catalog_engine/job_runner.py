"""
Brand Battle — Catalog Ingestion Job Runner
Orchestrates batch and asynchronous ingestion jobs.
Guarantees untrusted data staging, delta syncs via SHA-256 hashes,
resumable cursor pagination, and human-in-the-loop review queue routing.
"""

import hashlib
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

import models
from database import SessionLocal
from catalog_engine.schemas import NormalizedProductCandidate
from catalog_engine.base_adapter import BaseCatalogAdapter
from catalog_engine.adapters.flipkart_feed_adapter import FlipkartFeedAdapter
from catalog_engine.adapters.admin_import_adapter import AdminFileImportAdapter
from catalog_engine.deduplicator import CatalogDeduplicator
from catalog_engine.quality_scorer import ProductQualityScorer
from catalog_engine.resolver import ProductIdentityResolver
from knowledge_graph.kg_service import kg_service

logger = logging.getLogger("brandbattle.catalog.job_runner")


class CatalogJobRunner:
    """
    Executes and monitors catalog ingestion jobs across registered sources.
    """

    @classmethod
    def get_adapter(cls, source: models.CatalogSource, file_path: Optional[str] = None) -> BaseCatalogAdapter:
        """Instantiates the appropriate adapter for a CatalogSource."""
        if source.adapter_key == "flipkart_feed":
            return FlipkartFeedAdapter(source_id=source.id, source_name=source.name)
        elif source.adapter_key == "admin_import":
            return AdminFileImportAdapter(source_id=source.id, source_name=source.name, file_path=file_path)
        else:
            # Fallback to AdminFileImportAdapter
            return AdminFileImportAdapter(source_id=source.id, source_name=source.name, file_path=file_path)

    @classmethod
    def run_job(
        cls,
        source_id: int,
        job_type: str = "FULL_SYNC",
        file_path: Optional[str] = None,
        max_records: Optional[int] = None,
        batch_size: int = 50,
        db: Optional[Session] = None
    ) -> models.CatalogIngestionJob:
        """
        Executes a catalog ingestion job synchronously or as a background task.
        """
        own_session = False
        if db is None:
            db = SessionLocal()
            own_session = True

        try:
            source = db.get(models.CatalogSource, source_id)
            if not source:
                raise ValueError(f"Catalog source with ID {source_id} not found.")

            # Create or resume job record
            job = models.CatalogIngestionJob(
                source_id=source.id,
                job_type=job_type,
                status=models.JobStatus.RUNNING.value,
                started_at=datetime.now(timezone.utc),
                records_seen=0,
                records_created=0,
                records_updated=0,
                records_merged=0,
                records_reviewed=0,
                records_rejected=0,
                records_failed=0,
                error_summary=[],
            )
            db.add(job)
            db.commit()
            db.refresh(job)

            adapter = cls.get_adapter(source, file_path)
            cursor = None
            total_processed = 0

            while True:
                # Determine limit for this batch
                current_limit = batch_size
                if max_records and (total_processed + current_limit > max_records):
                    current_limit = max_records - total_processed
                if current_limit <= 0:
                    break

                # Fetch batch from adapter
                try:
                    records, next_cursor = adapter.fetch_batch(cursor=cursor, limit=current_limit)
                except Exception as e:
                    logger.error(f"Error fetching batch from adapter {adapter.adapter_key}: {e}")
                    cls._record_error(job, f"Fetch error at cursor {cursor}: {str(e)}")
                    break

                if not records:
                    break

                # Process batch within transaction
                for raw_item in records:
                    try:
                        cls._process_single_record(raw_item, adapter, source, job, db)
                    except Exception as e:
                        logger.error(f"Error processing record {raw_item.get('id')}: {e}")
                        job.records_failed += 1
                        cls._record_error(job, f"Processing error for item {raw_item.get('id')}: {str(e)}")

                total_processed += len(records)
                job.records_seen += len(records)
                cursor = next_cursor
                job.cursor = cursor
                db.commit()

                if not next_cursor or (max_records and total_processed >= max_records):
                    break

            # Mark job complete
            job.status = models.JobStatus.COMPLETED.value
            job.completed_at = datetime.now(timezone.utc)
            source.last_sync_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(job)
            logger.info(f"Ingestion job #{job.id} completed. Seen: {job.records_seen}, Created: {job.records_created}, Merged: {job.records_merged}, Reviewed: {job.records_reviewed}")
            return job

        except Exception as e:
            if db:
                db.rollback()
            logger.exception(f"Catalog ingestion job failed: {e}")
            raise
        finally:
            if own_session and db:
                db.close()

    @classmethod
    def _process_single_record(
        cls,
        raw_payload: Dict[str, Any],
        adapter: BaseCatalogAdapter,
        source: models.CatalogSource,
        job: models.CatalogIngestionJob,
        db: Session
    ):
        """Processes an individual raw record through staging, normalization, and KG resolution."""
        # 1. Compute deterministic content hash for delta sync
        payload_str = json.dumps(raw_payload, sort_keys=True, default=str)
        content_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        ext_id = str(raw_payload.get("id") or raw_payload.get("product_id") or raw_payload.get("sku") or content_hash[:16])

        # Check existing raw record
        existing_raw = db.query(models.RawCatalogRecord).filter(
            models.RawCatalogRecord.source_id == source.id,
            models.RawCatalogRecord.content_hash == content_hash
        ).first()

        if existing_raw and existing_raw.processing_status in (models.RawRecordStatus.PUBLISHED.value, models.RawRecordStatus.DUPLICATE.value):
            # Record already published and unchanged (Delta Sync Skip)
            job.records_updated += 1
            return

        # 2. Stage untrusted data in raw_catalog_records
        raw_record = models.RawCatalogRecord(
            source_id=source.id,
            external_id=ext_id,
            source_url=raw_payload.get("url") or raw_payload.get("product_url"),
            raw_payload=raw_payload,
            content_hash=content_hash,
            parser_version=getattr(adapter, "PARSER_VERSION", "v1.0"),
            processing_status=models.RawRecordStatus.RECEIVED.value,
        )
        db.add(raw_record)
        db.flush()

        # 3. Normalize into Candidate
        candidate: NormalizedProductCandidate = adapter.normalize(raw_record.id, raw_payload)
        raw_record.processing_status = models.RawRecordStatus.NORMALIZED.value

        # 4. Validate Candidate
        is_valid, val_errors = adapter.validate(candidate)
        candidate.validation_errors = val_errors
        if not is_valid:
            raw_record.processing_status = models.RawRecordStatus.REJECTED.value
            raw_record.failure_reason = "; ".join(val_errors)
            job.records_rejected += 1
            return

        # 5. Quality Scoring & Publishing Gate
        quality_score, is_publishable, score_reasons = ProductQualityScorer.evaluate(candidate)
        candidate.quality_score = quality_score
        candidate.is_publishable = is_publishable

        if not is_publishable:
            raw_record.processing_status = models.RawRecordStatus.REVIEW_REQUIRED.value
            raw_record.failure_reason = f"Quality score {quality_score}/100 below threshold 70"
            cls._route_to_review_queue(candidate, raw_record, "low_quality_score", db)
            job.records_reviewed += 1
            return

        # 6. Deduplication & Identity Resolution
        matched_master, confidence, match_reason = CatalogDeduplicator.resolve_candidate(candidate, db)

        if matched_master and confidence >= 0.98:
            # High confidence duplicate / existing product -> Merge offers & specifications
            raw_record.master_product_id = matched_master.id
            raw_record.processing_status = models.RawRecordStatus.PUBLISHED.value

            # Attach marketplace offer if present
            if candidate.has_offer and candidate.price is not None:
                cls._attach_offer(matched_master, candidate, confidence, db)

            job.records_merged += 1

        elif matched_master and (0.85 <= confidence < 0.98):
            # Ambiguous / Borderline candidate -> Route to Quarantine Review Queue
            raw_record.master_product_id = matched_master.id
            raw_record.processing_status = models.RawRecordStatus.REVIEW_REQUIRED.value
            raw_record.failure_reason = f"Borderline match confidence ({confidence:.3f}): {match_reason}"
            cls._route_to_review_queue(candidate, raw_record, "borderline_deduplication", db, matched_master.id, confidence)
            job.records_reviewed += 1

        else:
            # Distinct new product candidate -> Create canonical MasterProduct
            new_master = cls._create_canonical_master(candidate, db)
            raw_record.master_product_id = new_master.id
            raw_record.processing_status = models.RawRecordStatus.PUBLISHED.value

            # Attach marketplace offer if present
            if candidate.has_offer and candidate.price is not None:
                cls._attach_offer(new_master, candidate, 1.0, db)

            # Sync legacy Product table
            kg_service.sync_product_from_master(new_master, db)
            job.records_created += 1

    @classmethod
    def _create_canonical_master(cls, candidate: NormalizedProductCandidate, db: Session) -> models.MasterProduct:
        """Creates a new canonical MasterProduct with brand and category linkage."""
        brand = ProductIdentityResolver.resolve_brand(candidate.canonical_brand, db)
        category = ProductIdentityResolver.resolve_category(candidate.canonical_category, db)
        slug = ProductIdentityResolver.generate_unique_slug(candidate.canonical_name, db)

        master = models.MasterProduct(
            uuid=str(uuid.uuid4()),
            canonical_name=candidate.canonical_name,
            slug=slug,
            brand_id=brand.id,
            category_id=category.id,
            description=candidate.description,
            model_name=candidate.model_name or candidate.model_number,
            model_series=candidate.model_series,
            variant=candidate.variant_name,
            color_family=candidate.color,
            global_sku=candidate.gtin or candidate.ean or candidate.upc or candidate.sku,
            specifications=candidate.specifications,
            features=candidate.features,
            primary_image_url=candidate.primary_image_url,
            images=candidate.images,
            lowest_price=candidate.price,
            highest_price=candidate.original_price or candidate.price,
            average_rating=candidate.rating or 0.0,
            total_reviews=candidate.total_reviews or 0,
            confidence_score=1.0,
            completeness_score=candidate.quality_score,
            status=models.ProductLifecycleState.ACTIVE.value,
            is_verified=True,
            is_active=True,
        )
        db.add(master)
        db.flush()

        master.public_id = f"BB-PRD-{master.id:010d}"

        # Create GTIN attribute if valid
        if candidate.is_gtin_valid and (candidate.gtin or candidate.ean or candidate.upc):
            attr = models.ProductAttribute(
                master_product_id=master.id,
                attribute_name="gtin",
                attribute_value=candidate.gtin or candidate.ean or candidate.upc,
                attribute_type="text",
                is_searchable=True,
            )
            db.add(attr)

        return master

    @classmethod
    def _attach_offer(
        cls,
        master: models.MasterProduct,
        candidate: NormalizedProductCandidate,
        confidence: float,
        db: Session
    ) -> models.MarketplaceOffer:
        """Links or updates a MarketplaceOffer with strictly canonical INR currency."""
        marketplace = candidate.marketplace or "Direct"
        url = candidate.source_url or f"#{candidate.external_id}"

        offer = db.query(models.MarketplaceOffer).filter(
            models.MarketplaceOffer.master_product_id == master.id,
            models.MarketplaceOffer.marketplace == marketplace,
            models.MarketplaceOffer.url == url
        ).first()

        price = candidate.price or 0.0
        orig_price = candidate.original_price
        discount_pct = 0.0
        if orig_price and orig_price > price:
            discount_pct = round(((orig_price - price) / orig_price) * 100, 1)

        if offer:
            offer.price = price
            offer.original_price = orig_price
            offer.discount_percentage = discount_pct
            offer.currency = "INR"
            offer.is_available = candidate.availability
            offer.last_scraped = datetime.now(timezone.utc)
            offer.match_confidence = confidence
        else:
            offer = models.MarketplaceOffer(
                master_product_id=master.id,
                marketplace=marketplace,
                marketplace_product_id=candidate.external_id,
                title=candidate.clean_title,
                url=url,
                image_url=candidate.primary_image_url,
                price=price,
                original_price=orig_price,
                discount_percentage=discount_pct,
                currency="INR",
                seller_name=candidate.seller_name,
                stock_status=candidate.stock_status,
                is_available=candidate.availability,
                match_confidence=confidence,
                last_scraped=datetime.now(timezone.utc),
                status=models.OfferStatus.ACTIVE.value,
            )
            db.add(offer)

        # Update master lowest price
        if master.lowest_price is None or price < master.lowest_price:
            master.lowest_price = price
        master.offer_count = (master.offer_count or 0) + 1

        db.flush()
        return offer

    @classmethod
    def _route_to_review_queue(
        cls,
        candidate: NormalizedProductCandidate,
        raw_record: models.RawCatalogRecord,
        trigger_reason: str,
        db: Session,
        matched_master_id: Optional[int] = None,
        confidence: Optional[float] = None
    ):
        """Creates a quarantine ReviewQueueItem for human-in-the-loop inspection."""
        review_item = models.ReviewQueueItem(
            master_product_id=matched_master_id,
            trigger_reason=trigger_reason,
            priority="medium" if confidence and confidence >= 0.90 else "low",
            status=models.ReviewQueueStatus.PENDING.value,
            confidence_score=confidence or 0.0,
            metadata_json={
                "candidate_title": candidate.clean_title,
                "candidate_brand": candidate.canonical_brand,
                "candidate_category": candidate.canonical_category,
                "raw_record_id": raw_record.id,
                "source_name": candidate.source_name,
                "external_id": candidate.external_id,
                "quality_score": candidate.quality_score,
            }
        )
        db.add(review_item)
        db.flush()

    @classmethod
    def _record_error(cls, job: models.CatalogIngestionJob, error_msg: str):
        """Appends error message to job's error_summary list (capped at 20)."""
        summary = job.error_summary or []
        if isinstance(summary, str):
            try:
                summary = json.loads(summary)
            except Exception:
                summary = []
        summary.append({"timestamp": datetime.now(timezone.utc).isoformat(), "error": error_msg})
        job.error_summary = summary[-20:]
