"""
Brand Battle - Pipeline Monitoring & Metrics Collector
Tracks ingestion throughput, validation pass/fail rates, matching confidence distribution,
Knowledge Graph operations, and DLQ depth.
"""

from typing import Dict, Any
import time


class PipelineMonitor:
    """Real-time metrics aggregator for data pipeline and Knowledge Graph health."""

    def __init__(self):
        self.start_time = time.time()
        self.total_scraped = 0
        self.validation_passed = 0
        self.validation_failed = 0
        self.matched_existing = 0
        self.created_new_master = 0
        self.quality_passed = 0
        self.quality_failed = 0
        self.cache_invalidations = 0
        # Knowledge Graph metrics
        self.kg_masters_created = 0
        self.kg_masters_reused = 0
        self.kg_offers_created = 0
        self.kg_relationships_detected = 0
        self.kg_normalization_errors = 0
        self.kg_matching_failures = 0

    def record_ingest(self, count: int = 1):
        self.total_scraped += count

    def record_validation(self, success: bool):
        if success:
            self.validation_passed += 1
        else:
            self.validation_failed += 1

    def record_match(self, matched_existing: bool):
        if matched_existing:
            self.matched_existing += 1
        else:
            self.created_new_master += 1

    def record_quality(self, success: bool):
        if success:
            self.quality_passed += 1
        else:
            self.quality_failed += 1

    def record_cache_purge(self):
        self.cache_invalidations += 1

    # Knowledge Graph specific metrics
    def record_kg_master_created(self):
        self.kg_masters_created += 1

    def record_kg_master_reused(self):
        self.kg_masters_reused += 1

    def record_kg_offer_created(self):
        self.kg_offers_created += 1

    def record_kg_relationship(self, count: int = 1):
        self.kg_relationships_detected += count

    def record_kg_normalization_error(self):
        self.kg_normalization_errors += 1

    def record_kg_matching_failure(self):
        self.kg_matching_failures += 1

    def get_summary(self) -> Dict[str, Any]:
        uptime_seconds = round(time.time() - self.start_time, 1)
        return {
            "uptime_seconds": uptime_seconds,
            "total_scraped": self.total_scraped,
            "validation": {
                "passed": self.validation_passed,
                "failed": self.validation_failed,
                "pass_rate_pct": round((self.validation_passed / max(1, self.total_scraped)) * 100, 1)
            },
            "matching": {
                "matched_to_existing_master": self.matched_existing,
                "created_new_master": self.created_new_master,
            },
            "quality": {
                "passed": self.quality_passed,
                "failed": self.quality_failed,
            },
            "knowledge_graph": {
                "masters_created": self.kg_masters_created,
                "masters_reused": self.kg_masters_reused,
                "offers_created": self.kg_offers_created,
                "relationships_detected": self.kg_relationships_detected,
                "normalization_errors": self.kg_normalization_errors,
                "matching_failures": self.kg_matching_failures,
                "dedup_rate_pct": round(
                    (self.kg_masters_reused / max(1, self.kg_masters_created + self.kg_masters_reused)) * 100, 1
                ),
            },
            "cache_invalidations": self.cache_invalidations
        }


# Global pipeline monitor instance
pipeline_monitor = PipelineMonitor()
