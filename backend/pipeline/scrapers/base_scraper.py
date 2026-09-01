"""
Brand Battle - Abstract Base Scraper
Provides retry handling, rate limiting, exception isolation, metric tracking,
granular status codes, parser versioning, and health log recording for marketplace scrapers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger("brandbattle.scraper")


class RawProductItem(BaseModel):
    """Unified payload contract emitted by scrapers into the pipeline queue."""
    raw_title: str
    marketplace: str  # amazon, flipkart, myntra, ajio, croma, reliance_digital
    price: float
    original_price: Optional[float] = None
    currency: str = "INR"
    product_url: str
    image_url: Optional[str] = None
    brand_hint: Optional[str] = None
    category_hint: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    seller_name: Optional[str] = None
    availability: bool = True
    scraped_at: float = Field(default_factory=time.time)
    # Data Trust Hardening — scraper provenance
    marketplace_product_id: Optional[str] = None  # ASIN, Flipkart PID, etc.
    parser_version: Optional[str] = None
    source_method: str = "scraper"  # api, scraper, feed, manual


# ─── Scrape Result Status ─────────────────────────────────────────────

SCRAPE_STATUS_SUCCESS = "success"
SCRAPE_STATUS_PARTIAL = "partial_success"
SCRAPE_STATUS_NO_DATA = "no_data"
SCRAPE_STATUS_BLOCKED = "blocked"
SCRAPE_STATUS_TIMEOUT = "timeout"
SCRAPE_STATUS_PARSER_ERROR = "parser_error"
SCRAPE_STATUS_PRODUCT_NOT_FOUND = "product_not_found"
SCRAPE_STATUS_RATE_LIMITED = "rate_limited"
SCRAPE_STATUS_SOURCE_UNAVAILABLE = "source_unavailable"


@dataclass
class ScrapeResult:
    """Structured result from a scraper execution."""
    status: str
    items: List[RawProductItem] = field(default_factory=list)
    products_found: int = 0
    prices_extracted: int = 0
    images_extracted: int = 0
    failures: int = 0
    failure_reason: Optional[str] = None
    http_status: Optional[int] = None
    duration_ms: float = 0.0
    parser_version: Optional[str] = None


class BaseScraper(ABC):
    """Abstract base class for all marketplace data extraction workers."""

    PARSER_VERSION = "base_v1"

    def __init__(self, marketplace: str, rate_limit_delay: float = 1.0, max_retries: int = 3):
        self.marketplace = marketplace
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.success_count = 0
        self.failure_count = 0
        self.last_run_time: Optional[float] = None

    @abstractmethod
    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        """Scrape raw product listings from the target marketplace."""
        pass

    def run_safe(self, keyword_or_category: str) -> ScrapeResult:
        """
        Executes scraping with automatic retries, rate limiting, failure isolation,
        and structured result reporting including scraper health logging.
        """
        self.last_run_time = time.time()
        start_time = time.time()
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{self.marketplace}] Scraping '{keyword_or_category}' (Attempt {attempt}/{self.max_retries})")
                results = self.scrape(keyword_or_category)

                duration_ms = (time.time() - start_time) * 1000
                self.success_count += len(results)

                # Stamp parser version on every item
                for item in results:
                    item.parser_version = self.PARSER_VERSION

                products_found = len(results)
                prices_extracted = sum(1 for r in results if r.price > 0)
                images_extracted = sum(1 for r in results if r.image_url)

                status = SCRAPE_STATUS_SUCCESS if products_found > 0 else SCRAPE_STATUS_NO_DATA

                result = ScrapeResult(
                    status=status,
                    items=results,
                    products_found=products_found,
                    prices_extracted=prices_extracted,
                    images_extracted=images_extracted,
                    failures=0,
                    duration_ms=round(duration_ms, 1),
                    parser_version=self.PARSER_VERSION,
                )

                self._log_health(result)
                time.sleep(self.rate_limit_delay)
                return result

            except TimeoutError:
                last_error = "Timeout"
                logger.error(f"[{self.marketplace}] Timeout on attempt {attempt}")
                time.sleep(self.rate_limit_delay * attempt)
            except Exception as e:
                last_error = str(e)[:500]
                logger.error(f"[{self.marketplace}] Scrape failed on attempt {attempt}: {e}")
                time.sleep(self.rate_limit_delay * attempt)

        # All retries exhausted
        self.failure_count += 1
        duration_ms = (time.time() - start_time) * 1000

        result = ScrapeResult(
            status=SCRAPE_STATUS_SOURCE_UNAVAILABLE,
            items=[],
            products_found=0,
            prices_extracted=0,
            images_extracted=0,
            failures=self.max_retries,
            failure_reason=last_error,
            duration_ms=round(duration_ms, 1),
            parser_version=self.PARSER_VERSION,
        )

        self._log_health(result)
        return result

    def _log_health(self, result: ScrapeResult) -> None:
        """
        Writes a ScraperHealthLog record to the database.
        Silently skips if DB is unavailable (non-blocking).
        """
        try:
            from database import SessionLocal
            from models import ScraperHealthLog

            db = SessionLocal()
            try:
                log_entry = ScraperHealthLog(
                    marketplace=self.marketplace,
                    parser_version=result.parser_version,
                    started_at=datetime.fromtimestamp(self.last_run_time or time.time(), tz=timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    status=result.status,
                    products_found=result.products_found,
                    prices_extracted=result.prices_extracted,
                    images_extracted=result.images_extracted,
                    failures=result.failures,
                    failure_reason=result.failure_reason,
                    http_status=result.http_status,
                    duration_ms=result.duration_ms,
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.warning(f"Failed to log scraper health: {e}")
            finally:
                db.close()
        except Exception:
            pass  # Non-blocking — never break the scraper for logging failures

    def get_health_status(self) -> Dict[str, Any]:
        """Returns health metrics for scraper monitoring."""
        return {
            "marketplace": self.marketplace,
            "parser_version": self.PARSER_VERSION,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_run_time": self.last_run_time,
            "is_healthy": self.failure_count < 5
        }
