"""
Brand Battle - Abstract Base Scraper
Provides retry handling, rate limiting, exception isolation, and metric tracking for marketplace scrapers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
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


class BaseScraper(ABC):
    """Abstract base class for all marketplace data extraction workers."""

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

    def run_safe(self, keyword_or_category: str) -> List[RawProductItem]:
        """Executes scraping with automatic retries, rate limiting, and failure isolation."""
        self.last_run_time = time.time()
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{self.marketplace}] Scraping '{keyword_or_category}' (Attempt {attempt}/{self.max_retries})")
                results = self.scrape(keyword_or_category)
                self.success_count += len(results)
                time.sleep(self.rate_limit_delay)
                return results
            except Exception as e:
                logger.error(f"[{self.marketplace}] Scrape failed on attempt {attempt}: {e}")
                time.sleep(self.rate_limit_delay * attempt)
        
        self.failure_count += 1
        return []

    def get_health_status(self) -> Dict[str, Any]:
        """Returns health metrics for scraper monitoring."""
        return {
            "marketplace": self.marketplace,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_run_time": self.last_run_time,
            "is_healthy": self.failure_count < 5
        }
