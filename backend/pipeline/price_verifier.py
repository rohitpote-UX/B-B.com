"""
Brand Battle — Price Verification Engine
Determines verification status, confidence scores, and detects price anomalies
before accepting scraped/fetched prices into the production database.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from data_freshness import (
    determine_verification_status,
    get_freshness_display,
    ANOMALY_THRESHOLD_PCT,
)

logger = logging.getLogger("brandbattle.price_verifier")


@dataclass
class PriceVerificationResult:
    """Structured result from price verification."""
    verification_status: str  # verified, recently_verified, stale, unverified, failed_verification
    confidence_score: float   # 0.0 - 1.0
    is_anomaly: bool
    anomaly_type: Optional[str]  # sudden_drop, sudden_spike, impossible_price
    freshness_display: str    # Human-readable: "Verified 4 min ago"
    absolute_difference: float
    percentage_difference: float
    accepted: bool            # Whether the price should be committed to DB


class PriceVerifier:
    """
    Determines verification status and confidence for incoming price observations.
    Implements anomaly detection before accepting prices into the database.
    """

    def __init__(self, anomaly_threshold_pct: float = ANOMALY_THRESHOLD_PCT):
        self.anomaly_threshold_pct = anomaly_threshold_pct

    def verify_price(
        self,
        new_price: float,
        previous_price: Optional[float],
        marketplace: str,
        source_method: str = "scraper",
        original_price: Optional[float] = None,
        currency: str = "INR",
        previous_currency: Optional[str] = "INR",
    ) -> PriceVerificationResult:
        """
        Validates an incoming price observation against the previous known price.

        Anomaly detection rules:
        - Price change > anomaly_threshold_pct triggers anomaly flag
        - Raw cross-currency comparisons (INR vs USD) trigger currency_error
        - Price <= 0 is impossible
        - Price > 10,000,000 is impossible
        - Original price < current price is suspicious

        Returns a PriceVerificationResult with acceptance decision.
        """
        now = datetime.now(timezone.utc)

        # Impossible price guard
        if new_price <= 0 or new_price > 10_000_000:
            return PriceVerificationResult(
                verification_status="failed_verification",
                confidence_score=0.0,
                is_anomaly=True,
                anomaly_type="impossible_price",
                freshness_display=get_freshness_display(now),
                absolute_difference=0.0,
                percentage_difference=0.0,
                accepted=False,
            )

        # Calculate difference from previous price
        abs_diff = 0.0
        pct_diff = 0.0
        is_anomaly = False
        anomaly_type = None

        if previous_price is not None and previous_price > 0:
            norm_prev = previous_price
            # Normalize to same currency for comparison if cross-currency detected
            if currency and previous_currency and currency != previous_currency:
                if currency == "INR" and previous_currency == "USD":
                    norm_prev = previous_price * 84.0
                elif currency == "USD" and previous_currency == "INR":
                    norm_prev = previous_price / 84.0

            # Detect raw un-normalized cross-currency bug (e.g. 179900 INR vs 2141.67 without currency tag)
            ratio = previous_price / new_price if new_price > 0 else 0
            inv_ratio = new_price / previous_price if previous_price > 0 else 0
            if (75.0 <= ratio <= 95.0) or (75.0 <= inv_ratio <= 95.0):
                is_anomaly = True
                anomaly_type = "currency_error"
                abs_diff = abs(new_price - norm_prev)
                pct_diff = (abs_diff / norm_prev) * 100.0 if norm_prev > 0 else 0.0
            else:
                abs_diff = abs(new_price - norm_prev)
                pct_diff = (abs_diff / norm_prev) * 100.0 if norm_prev > 0 else 0.0

                if pct_diff > self.anomaly_threshold_pct:
                    is_anomaly = True
                    if new_price < norm_prev:
                        anomaly_type = "sudden_drop"
                    else:
                        anomaly_type = "sudden_spike"

        # Confidence scoring
        confidence = self._calculate_confidence(
            new_price=new_price,
            previous_price=previous_price,
            pct_diff=pct_diff,
            source_method=source_method,
            is_anomaly=is_anomaly,
        )

        # Determine acceptance
        accepted = not is_anomaly  # Anomalies require secondary verification

        # Verification status for fresh observation
        verification_status = "verified" if accepted else "partially_verified"

        return PriceVerificationResult(
            verification_status=verification_status,
            confidence_score=confidence,
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            freshness_display=get_freshness_display(now),
            absolute_difference=round(abs_diff, 2),
            percentage_difference=round(pct_diff, 2),
            accepted=accepted,
        )

    def _calculate_confidence(
        self,
        new_price: float,
        previous_price: Optional[float],
        pct_diff: float,
        source_method: str,
        is_anomaly: bool,
    ) -> float:
        """
        Calculates a confidence score (0.0 - 1.0) for the price observation.

        Factors:
        - Source method reliability (api > feed > scraper > manual)
        - Price stability (small changes = higher confidence)
        - Anomaly flag (reduces confidence)
        """
        # Base confidence by source method
        source_confidence = {
            "api": 0.95,
            "feed": 0.90,
            "scraper": 0.80,
            "manual": 0.70,
            "seed": 0.50,
        }
        base = source_confidence.get(source_method, 0.60)

        # Stability bonus (if price is close to previous)
        if previous_price is not None and previous_price > 0:
            if pct_diff <= 2.0:
                base = min(1.0, base + 0.10)
            elif pct_diff <= 5.0:
                base = min(1.0, base + 0.05)
            elif pct_diff > 20.0:
                base = max(0.3, base - 0.15)

        # Anomaly penalty
        if is_anomaly:
            base = max(0.2, base - 0.30)

        return round(base, 2)

    def detect_price_anomaly(
        self,
        product_id: int,
        new_price: float,
        previous_price: Optional[float],
        marketplace: str,
        currency: str = "INR",
        previous_currency: Optional[str] = "INR",
    ) -> Optional[Dict[str, Any]]:
        """
        Returns anomaly metadata dict if an anomaly is detected, else None.
        This dict is used to create a PriceAnomalyLog record.
        """
        if previous_price is None or previous_price <= 0:
            return None

        if new_price <= 0:
            return {
                "product_id": product_id,
                "marketplace": marketplace,
                "previous_price": previous_price,
                "new_price": new_price,
                "absolute_difference": round(previous_price, 2),
                "percentage_difference": 100.0,
                "anomaly_type": "impossible_price",
            }

        norm_prev = previous_price
        if currency and previous_currency and currency != previous_currency:
            if currency == "INR" and previous_currency == "USD":
                norm_prev = previous_price * 84.0
            elif currency == "USD" and previous_currency == "INR":
                norm_prev = previous_price / 84.0

        ratio = previous_price / new_price if new_price > 0 else 0
        inv_ratio = new_price / previous_price if previous_price > 0 else 0
        if (75.0 <= ratio <= 95.0) or (75.0 <= inv_ratio <= 95.0):
            abs_diff = abs(new_price - norm_prev)
            pct_diff = (abs_diff / norm_prev) * 100.0 if norm_prev > 0 else 0.0
            return {
                "product_id": product_id,
                "marketplace": marketplace,
                "previous_price": previous_price,
                "new_price": new_price,
                "absolute_difference": round(abs_diff, 2),
                "percentage_difference": round(pct_diff, 2),
                "anomaly_type": "currency_error",
            }

        abs_diff = abs(new_price - norm_prev)
        pct_diff = (abs_diff / norm_prev) * 100.0 if norm_prev > 0 else 0.0

        if pct_diff <= self.anomaly_threshold_pct:
            return None

        anomaly_type = "sudden_drop" if new_price < norm_prev else "sudden_spike"

        return {
            "product_id": product_id,
            "marketplace": marketplace,
            "previous_price": previous_price,
            "new_price": new_price,
            "absolute_difference": round(abs_diff, 2),
            "percentage_difference": round(pct_diff, 2),
            "anomaly_type": anomaly_type,
        }


# Singleton
price_verifier = PriceVerifier()
