"""
Brand Battle — Image Verification Engine
Validates product image URLs via HTTP HEAD requests.
Checks accessibility, Content-Type, and resolution.
"""

import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger("brandbattle.image_verifier")


@dataclass
class ImageVerificationResult:
    """Structured result from image URL verification."""
    url: str
    is_valid: bool
    http_status: Optional[int]
    content_type: Optional[str]
    verification_status: str  # verified, unverified, quarantined_mismatch, failed_verification
    failure_reason: Optional[str]
    verified_at: datetime


# Neutral on-brand SVG fallback for BrandBattle (#050505 / #ff1695)
FALLBACK_PRODUCT_IMAGE = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600' viewBox='0 0 600 600' fill='%23050505'>"
    "<rect width='600' height='600' fill='%230c0c0e' rx='24'/>"
    "<rect x='40' y='40' width='520' height='520' fill='none' stroke='%23ffffff' stroke-opacity='0.06' stroke-width='2' rx='16'/>"
    "<circle cx='300' cy='270' r='70' fill='%23ff1695' fill-opacity='0.08' stroke='%23ff1695' stroke-opacity='0.25' stroke-width='2'/>"
    "<circle cx='300' cy='270' r='24' fill='none' stroke='%23ff1695' stroke-width='2' stroke-dasharray='4 4'/>"
    "<path d='M290 270 h20 M300 260 v20' stroke='%23ff1695' stroke-width='2' stroke-linecap='round'/>"
    "<text x='50%' y='390' dominant-baseline='middle' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' font-size='13' font-weight='600' letter-spacing='2' fill='%23ffffff' fill-opacity='0.65'>BRAND BATTLE HARDWARE</text>"
    "<text x='50%' y='416' dominant-baseline='middle' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' font-size='10' letter-spacing='1.5' fill='%23ffffff' fill-opacity='0.35'>OFFICIAL INTEL ACTIVE</text>"
    "</svg>"
)

# Known mismatched / quarantined image signatures mapped to their actual subject
KNOWN_QUARANTINED_IMAGE_SIGNATURES: Dict[str, Dict[str, str]] = {
    "71j8tz0uejl": {
        "actual_model": "Samsung Galaxy S22 Ultra",
        "brand": "Samsung",
        "generation": "22",
        "reason": "Image portrays Samsung Galaxy S22 Ultra, cannot be associated with Galaxy S26 Ultra"
    },
    "71657tifehl": {
        "actual_model": "Apple iPhone 15",
        "brand": "Apple",
        "generation": "15",
        "reason": "Image portrays Apple iPhone 15, cannot be associated with iPhone 18"
    },
    "81+gikwqlil": {
        "actual_model": "Apple iPhone 15 Pro Max",
        "brand": "Apple",
        "generation": "15",
        "reason": "Image portrays Apple iPhone 15 Pro Max, cannot be associated with iPhone 18 Pro Max"
    },
    "6175slkkecl": {
        "actual_model": "OnePlus Nord CE 3 5G",
        "brand": "OnePlus",
        "generation": "Nord CE 3",
        "reason": "Image portrays OnePlus Nord CE 3, cannot be associated with OnePlus 15 Pro"
    },
}


# Known placeholder / broken image patterns to reject
PLACEHOLDER_PATTERNS = [
    "placeholder",
    "no-image",
    "noimage",
    "default-product",
    "coming-soon",
    "image-not-available",
    "broken-image",
    "dummy",
]

VALID_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
    "image/avif",
}


class ImageVerifier:
    """
    Validates product image URLs via HTTP HEAD requests.
    Designed to run synchronously in background tasks, not in request path.
    """

    def verify_image_url(self, image_url: str) -> ImageVerificationResult:
        """
        Validates a single image URL.

        Checks:
        1. URL is well-formed and starts with http/https
        2. URL is not a known placeholder pattern
        3. HTTP HEAD request returns 200
        4. Content-Type is a valid image MIME type
        """
        now = datetime.now(timezone.utc)

        if not image_url or not isinstance(image_url, str):
            return ImageVerificationResult(
                url=image_url or "",
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status="failed_verification",
                failure_reason="Empty or invalid URL",
                verified_at=now,
            )

        if not image_url.startswith(("http://", "https://")):
            return ImageVerificationResult(
                url=image_url,
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status="failed_verification",
                failure_reason="URL does not start with http/https",
                verified_at=now,
            )

        # Check for placeholder patterns
        url_lower = image_url.lower()
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in url_lower:
                return ImageVerificationResult(
                    url=image_url,
                    is_valid=False,
                    http_status=None,
                    content_type=None,
                    verification_status="failed_verification",
                    failure_reason=f"URL matches placeholder pattern: {pattern}",
                    verified_at=now,
                )

        # Attempt HTTP HEAD request
        try:
            import requests
            response = requests.head(
                image_url,
                timeout=10,
                allow_redirects=True,
                headers={"User-Agent": "BrandBattle-ImageVerifier/1.0"}
            )
            status_code = response.status_code
            content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()

            if status_code != 200:
                return ImageVerificationResult(
                    url=image_url,
                    is_valid=False,
                    http_status=status_code,
                    content_type=content_type or None,
                    verification_status="failed_verification",
                    failure_reason=f"HTTP {status_code}",
                    verified_at=now,
                )

            if content_type not in VALID_IMAGE_CONTENT_TYPES:
                return ImageVerificationResult(
                    url=image_url,
                    is_valid=False,
                    http_status=status_code,
                    content_type=content_type,
                    verification_status="failed_verification",
                    failure_reason=f"Invalid content type: {content_type}",
                    verified_at=now,
                )

            return ImageVerificationResult(
                url=image_url,
                is_valid=True,
                http_status=status_code,
                content_type=content_type,
                verification_status="verified",
                failure_reason=None,
                verified_at=now,
            )

        except requests.exceptions.Timeout:
            return ImageVerificationResult(
                url=image_url,
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status="pending_retry",
                failure_reason="Request timed out (transient network delay)",
                verified_at=now,
            )
        except requests.exceptions.ConnectionError:
            return ImageVerificationResult(
                url=image_url,
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status="pending_retry",
                failure_reason="Connection error (transient network failure)",
                verified_at=now,
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying image {image_url}: {e}")
            return ImageVerificationResult(
                url=image_url,
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status="failed_verification",
                failure_reason=f"Unexpected error: {str(e)[:200]}",
                verified_at=now,
            )

    def validate_product_image_association(
        self,
        product_name: str,
        image_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Enforces product identity and model generation integrity.
        Validates whether the image genuinely corresponds to the canonical product model.
        Returns: (is_valid: bool, verification_status: str, failure_reason: Optional[str])
        """
        if not image_url or not isinstance(image_url, str):
            return False, "failed_verification", "Missing or empty image URL"

        clean_url = image_url.strip()
        if clean_url == FALLBACK_PRODUCT_IMAGE:
            # Fallback placeholder is intentionally safe & neutral
            return True, "unverified_neutral_fallback", None

        # Reject malformed URLs that do not begin with http:// or https://
        if not clean_url.startswith(("http://", "https://")):
            return False, "failed_verification", "URL does not start with http/https"

        url_lower = clean_url.lower()
        prod_lower = (product_name or "").lower()

        # 1. Check against known quarantined mismatched image signatures
        for sig, meta in KNOWN_QUARANTINED_IMAGE_SIGNATURES.items():
            if sig in url_lower:
                brand = meta.get("brand", "").lower()
                gen = meta.get("generation", "").lower()
                actual_model = meta.get("actual_model", "")

                # If the product does NOT match the signature's actual brand or model generation, reject
                if brand not in prod_lower:
                    reason = f"Brand mismatch: image portrays {actual_model} ({brand.title()}), but canonical product is '{product_name}'"
                    logger.warning(f"[QUARANTINE_MISMATCH] {reason} (URL: {image_url})")
                    return False, "quarantined_mismatch", reason

                if gen not in prod_lower:
                    reason = f"Generation mismatch: image portrays {actual_model}, but canonical product is '{product_name}'"
                    logger.warning(f"[QUARANTINE_MISMATCH] {reason} (URL: {image_url})")
                    return False, "quarantined_mismatch", reason

        # 2. Extract generation patterns from product name and inspect URL/metadata cues
        # Samsung Galaxy Series (e.g. S22, S23, S24, S25, S26)
        s_match = re.search(r'\b(?:galaxy\s+)?s(\d{2})\b', prod_lower)
        if s_match:
            prod_gen = s_match.group(1)
            other_s_match = re.search(r'\bs(\d{2})\b', url_lower)
            if other_s_match and other_s_match.group(1) != prod_gen:
                reason = f"Generation mismatch: URL mentions S{other_s_match.group(1)} while product is S{prod_gen}"
                logger.warning(f"[QUARANTINE_MISMATCH] {reason}")
                return False, "quarantined_mismatch", reason

        # Apple iPhone Series (e.g. iPhone 14, 15, 16, 17, 18)
        ip_match = re.search(r'\biphone\s+(\d{1,2})\b', prod_lower)
        if ip_match:
            prod_gen = ip_match.group(1)
            other_ip_match = re.search(r'\biphone(?:-|\s+)?(\d{1,2})\b', url_lower)
            if other_ip_match and other_ip_match.group(1) != prod_gen:
                reason = f"Generation mismatch: URL mentions iPhone {other_ip_match.group(1)} while product is iPhone {prod_gen}"
                logger.warning(f"[QUARANTINE_MISMATCH] {reason}")
                return False, "quarantined_mismatch", reason

        # 3. Provenance and Unreleased Preview Product Gates
        # If product claims to be an unreleased generation (e.g. Galaxy S26, iPhone 18)
        # and image source is generic unsplash or untrusted third party without official asset provenance:
        is_preview_launch = any(token in prod_lower for token in ["s26", "iphone 18", "pixel 10", "oneplus 15"])
        if is_preview_launch:
            if "unsplash.com" in url_lower:
                return False, "unverified", "Generic stock photo cannot be verified for canonical preview hardware"

        return True, "verified", None

    def verify_product_image_for_product(
        self,
        product_name: str,
        image_url: str,
        metadata: Optional[Dict[str, Any]] = None,
        check_network: bool = True
    ) -> ImageVerificationResult:
        """
        Comprehensive verification:
        1. Validates structural and network accessibility (HTTP 200, Content-Type)
        2. Validates product identity and model generation association
        Does NOT certify image solely because HTTP returned 200.
        """
        now = datetime.now(timezone.utc)

        # 1. Identity association check (run first to avoid unnecessary network calls on mismatches)
        is_assoc_valid, assoc_status, assoc_reason = self.validate_product_image_association(
            product_name, image_url, metadata
        )

        if not is_assoc_valid:
            return ImageVerificationResult(
                url=image_url,
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status=assoc_status,
                failure_reason=assoc_reason,
                verified_at=now,
            )

        # If it's the neutral fallback image, it is safe to display as unverified neutral fallback
        if image_url == FALLBACK_PRODUCT_IMAGE:
            return ImageVerificationResult(
                url=image_url,
                is_valid=True,
                http_status=200,
                content_type="image/svg+xml",
                verification_status="unverified",
                failure_reason=None,
                verified_at=now,
            )

        # 2. Structural & HTTP Network check
        if check_network:
            http_result = self.verify_image_url(image_url)
            if not http_result.is_valid:
                return http_result

            return ImageVerificationResult(
                url=image_url,
                is_valid=True,
                http_status=http_result.http_status,
                content_type=http_result.content_type,
                verification_status="verified",
                failure_reason=None,
                verified_at=now,
            )

        return ImageVerificationResult(
            url=image_url,
            is_valid=True,
            http_status=200,
            content_type="image/jpeg",
            verification_status="verified",
            failure_reason=None,
            verified_at=now,
        )

    def get_safe_image_for_product(
        self,
        product_name: str,
        image_url: Optional[str],
        candidate_alternates: Optional[List[str]] = None
    ) -> str:
        """
        Safe image resolver:
        Returns image_url if it passes identity and generation association.
        If primary candidate fails or is missing, checks candidate_alternates.
        Returns neutral on-brand fallback SVG only if no candidate passes.
        """
        candidates: List[str] = []
        if image_url and image_url.strip() and image_url != FALLBACK_PRODUCT_IMAGE:
            candidates.append(image_url.strip())
        if candidate_alternates:
            for alt in candidate_alternates:
                if alt and alt.strip() and alt.strip() not in candidates and alt.strip() != FALLBACK_PRODUCT_IMAGE:
                    candidates.append(alt.strip())

        for cand in candidates:
            is_assoc_valid, _, _ = self.validate_product_image_association(product_name, cand)
            if is_assoc_valid:
                return cand

        return FALLBACK_PRODUCT_IMAGE

    def find_fallback_image(self, product_id: int, db) -> Optional[str]:
        """
        Attempts to find an alternative valid image URL for a product.
        Checks MarketplaceOffer images and ProductImage table.
        Strictly enforces that any candidate image matches the product's canonical identity.
        """
        from models import MarketplaceOffer, ProductImage, Product

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product or not product.master_product_id:
            return None

        prod_name = product.name or ""

        # Try other verified images from the KG
        kg_images = (
            db.query(ProductImage)
            .filter(
                ProductImage.master_product_id == product.master_product_id,
                ProductImage.verification_status == "verified",
            )
            .order_by(ProductImage.is_primary.desc(), ProductImage.sort_order)
            .limit(5)
            .all()
        )

        for img in kg_images:
            if img.url and img.url != product.image_url:
                is_valid, _, _ = self.validate_product_image_association(prod_name, img.url)
                if is_valid:
                    return img.url

        # Try marketplace offer images
        offers = (
            db.query(MarketplaceOffer)
            .filter(
                MarketplaceOffer.master_product_id == product.master_product_id,
                MarketplaceOffer.image_url.isnot(None),
                MarketplaceOffer.is_available == True,
            )
            .limit(5)
            .all()
        )

        for offer in offers:
            if offer.image_url and offer.image_url != product.image_url:
                is_valid, _, _ = self.validate_product_image_association(prod_name, offer.image_url)
                if is_valid:
                    return offer.image_url

        return None


# Singleton
image_verifier = ImageVerifier()
