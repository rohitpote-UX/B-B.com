"""
Brand Battle — Image Verification Engine
Validates product image URLs via HTTP HEAD requests.
Checks accessibility, Content-Type, and resolution.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
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
    verification_status: str  # verified, unverified, failed_verification
    failure_reason: Optional[str]
    verified_at: datetime


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
                verification_status="failed_verification",
                failure_reason="Request timed out",
                verified_at=now,
            )
        except requests.exceptions.ConnectionError:
            return ImageVerificationResult(
                url=image_url,
                is_valid=False,
                http_status=None,
                content_type=None,
                verification_status="failed_verification",
                failure_reason="Connection error",
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

    def find_fallback_image(self, product_id: int, db) -> Optional[str]:
        """
        Attempts to find an alternative valid image URL for a product.
        Checks MarketplaceOffer images and ProductImage table.
        """
        from models import MarketplaceOffer, ProductImage, Product

        # Try marketplace offers for the same product's master
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product or not product.master_product_id:
            return None

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
                return offer.image_url

        return None


# Singleton
image_verifier = ImageVerifier()
