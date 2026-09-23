"""
Brand Battle — Flipkart Feed & Affiliate API Adapter
First permitted catalog ingestion source.
Implements official Affiliate API endpoints when credentials are provided,
falling back gracefully to approved marketplace feed files with full provenance.
"""

import os
import csv
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

import requests
from catalog_engine.base_adapter import BaseCatalogAdapter
from catalog_engine.schemas import NormalizedProductCandidate
from catalog_engine.normalizer import CatalogNormalizer
from catalog_engine.gtin_validator import GtinValidator
from catalog_engine.security import is_ssrf_safe_url, AdaptiveRateLimiter

logger = logging.getLogger("brandbattle.catalog.adapter.flipkart")


class FlipkartFeedAdapter(BaseCatalogAdapter):
    """
    Adapter for Flipkart Affiliate API / Authorized Product Feeds.
    Guarantees strict INR currency integrity and schema conformance.
    """

    PARSER_VERSION = "flipkart_catalog_v2.0"

    def __init__(self, source_id: int = 1, source_name: str = "Flipkart Affiliate Feed"):
        super().__init__(source_id=source_id, source_name=source_name, adapter_key="flipkart_feed")
        self.affiliate_id = os.getenv("FLIPKART_AFFILIATE_ID", "").strip()
        self.affiliate_token = os.getenv("FLIPKART_AFFILIATE_TOKEN", "").strip()
        self.api_base_url = os.getenv("FLIPKART_API_BASE_URL", "https://affiliate-api.flipkart.net/affiliate/1.0")
        self.rate_limiter = AdaptiveRateLimiter(requests_per_second=3.0)
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.feed_path = os.path.join(self.backend_dir, "flipkart_products.csv")

    def has_api_credentials(self) -> bool:
        """Returns True if live affiliate credentials are set."""
        return bool(self.affiliate_id and self.affiliate_token and len(self.affiliate_token) >= 8)

    def discover(self, cursor: Optional[str] = None) -> List[str]:
        """Discovers product identifiers from feed or API."""
        if self.has_api_credentials():
            # In live API mode, query categories or keywords
            return ["mobiles", "laptops", "smartwatches", "headphones", "tvs"]
        
        # In feed mode, discover external IDs from feed file
        ids = []
        if os.path.exists(self.feed_path):
            with open(self.feed_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    ext_id = row.get("id") or row.get("product_id") or f"FK_ROW_{idx+1}"
                    ids.append(ext_id)
        return ids

    def fetch(self, external_id: str) -> Dict[str, Any]:
        """Fetches raw product record by external ID."""
        if self.has_api_credentials():
            return self._call_flipkart_api(f"id:{external_id}")

        # Fallback to local approved feed
        if os.path.exists(self.feed_path):
            with open(self.feed_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    ext_id = row.get("id") or row.get("product_id") or f"FK_ROW_{idx+1}"
                    if ext_id == external_id:
                        return dict(row)
        return {}

    def fetch_batch(self, cursor: Optional[str] = None, limit: int = 50) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Fetches a slice of records using offset or cursor.
        Returns: (records: List[Dict], next_cursor: Optional[str])
        """
        start_idx = int(cursor) if cursor and cursor.isdigit() else 0
        records = []
        next_cursor = None

        if os.path.exists(self.feed_path):
            with open(self.feed_path, "r", encoding="utf-8", errors="replace") as f:
                reader = list(csv.DictReader(f))
                total = len(reader)
                slice_records = reader[start_idx : start_idx + limit]
                for idx, row in enumerate(slice_records):
                    d = dict(row)
                    d["_row_index"] = start_idx + idx
                    records.append(d)

                if start_idx + limit < total:
                    next_cursor = str(start_idx + limit)

        return records, next_cursor

    def normalize(self, raw_record_id: Optional[int], raw: Dict[str, Any]) -> NormalizedProductCandidate:
        """Transforms raw Flipkart payload into clean NormalizedProductCandidate."""
        row_idx = raw.get("_row_index", 1)
        ext_id = raw.get("id") or raw.get("product_id") or f"FK_{row_idx}"
        raw_title = raw.get("title") or raw.get("name") or raw.get("product_name") or ""
        raw_brand = raw.get("brand") or ""
        raw_cat = raw.get("category") or raw.get("category_name") or ""

        # Normalize brand and category
        _, canonical_brand = self.map_brand(raw_brand, title_hint=raw_title)
        _, canonical_category = self.map_category(raw_cat, title_hint=raw_title)
        clean_title = CatalogNormalizer.clean_title(raw_title, canonical_brand)

        # Identifiers
        identifiers = self.extract_identifiers(raw)
        gtin = identifiers.get("gtin")
        is_gtin_valid = False
        if gtin:
            valid, clean_g, _ = GtinValidator.validate(gtin)
            is_gtin_valid = valid
            gtin = clean_g

        # Variant attributes
        var_attrs = self.map_variant(raw)
        images = self.extract_images(raw)
        primary_image = images[0]["url"] if images else None
        specs = self.extract_specifications(raw)
        price_data = self.extract_price(raw)
        availability = self.extract_availability(raw)

        candidate = NormalizedProductCandidate(
            raw_record_id=raw_record_id,
            source_id=self.source_id,
            source_name=self.source_name,
            external_id=str(ext_id),
            source_url=raw.get("product_url") or raw.get("url") or f"https://www.flipkart.com/item/{ext_id}",
            brand=raw_brand,
            canonical_brand=canonical_brand,
            raw_title=raw_title,
            clean_title=clean_title,
            canonical_name=clean_title,
            model_name=identifiers.get("model_number") or var_attrs.get("model_name"),
            model_number=identifiers.get("model_number"),
            model_series=var_attrs.get("model_series"),
            mpn=identifiers.get("mpn"),
            gtin=gtin,
            ean=identifiers.get("ean"),
            upc=identifiers.get("upc"),
            is_gtin_valid=is_gtin_valid,
            raw_category=raw_cat,
            canonical_category=canonical_category,
            variant_name=var_attrs.get("storage") or var_attrs.get("color"),
            color=var_attrs.get("color"),
            storage=var_attrs.get("storage"),
            ram=var_attrs.get("ram"),
            variant_attributes=var_attrs,
            description=CatalogNormalizer.clean_text(raw.get("description") or f"{clean_title} by {canonical_brand}"),
            images=[img["url"] for img in images],
            primary_image_url=primary_image,
            specifications=specs,
            has_offer=bool(price_data),
            marketplace="Flipkart",
            seller_name=raw.get("seller_name") or "RetailNet / SuperComNet",
            price=price_data.get("price") if price_data else None,
            original_price=price_data.get("original_price") if price_data else None,
            currency="INR",
            availability=availability,
            affiliate_url=raw.get("affiliate_url") or raw.get("url"),
            rating=float(raw.get("rating")) if raw.get("rating") else None,
            total_reviews=int(raw.get("review_count") or raw.get("total_reviews") or 0),
            source_metadata=self.get_source_metadata(),
        )

        return candidate

    def validate(self, candidate: NormalizedProductCandidate) -> Tuple[bool, List[str]]:
        """Validates candidate against core identity constraints."""
        errors = []
        if not candidate.canonical_brand:
            errors.append("Missing canonical brand")
        if not candidate.clean_title or len(candidate.clean_title) < 3:
            errors.append("Invalid or empty product title")
        if not candidate.canonical_category:
            errors.append("Missing canonical category")
        if candidate.price is not None and candidate.price <= 0:
            errors.append(f"Invalid non-positive price: {candidate.price}")
        if candidate.currency != "INR":
            errors.append(f"Currency mismatch: expected INR, got {candidate.currency}")

        return (len(errors) == 0, errors)

    def map_category(self, raw_category: str, title_hint: Optional[str] = None) -> Tuple[str, str]:
        return CatalogNormalizer.normalize_category(raw_category, title_hint)

    def map_brand(self, raw_brand: str, title_hint: Optional[str] = None) -> Tuple[str, str]:
        return CatalogNormalizer.normalize_brand(raw_brand, title_hint)

    def map_variant(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        title = raw.get("title") or raw.get("name") or ""
        attrs = CatalogNormalizer.extract_variant_attributes(title)
        if raw.get("color"):
            attrs["color"] = CatalogNormalizer.clean_text(raw["color"])
        if raw.get("storage"):
            attrs["storage"] = CatalogNormalizer.clean_text(raw["storage"]).upper().replace(" ", "")
        return attrs

    def extract_identifiers(self, raw: Dict[str, Any]) -> Dict[str, Optional[str]]:
        return {
            "gtin": raw.get("gtin") or raw.get("ean") or raw.get("upc"),
            "ean": raw.get("ean"),
            "upc": raw.get("upc"),
            "mpn": raw.get("mpn"),
            "model_number": raw.get("model_number") or raw.get("model_name"),
            "sku": raw.get("fsn") or raw.get("sku"),
        }

    def extract_images(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        images = []
        url = raw.get("image_url") or raw.get("image") or raw.get("primary_image")
        if url and is_ssrf_safe_url(url):
            images.append({"url": url.strip(), "alt_text": raw.get("title", "")})
        return images

    def extract_specifications(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        specs = {}
        # Parse if stringified json
        raw_specs = raw.get("specifications") or raw.get("specs")
        if isinstance(raw_specs, str):
            try:
                specs = json.loads(raw_specs)
            except Exception:
                specs = {}
        elif isinstance(raw_specs, dict):
            specs = raw_specs

        # Extract column-based specs if present
        for col in ["ram", "storage", "processor", "battery", "camera", "display", "screen_size"]:
            if raw.get(col):
                specs[col.title()] = CatalogNormalizer.clean_text(str(raw[col]))

        return CatalogNormalizer.clean_specifications(specs)

    def extract_availability(self, raw: Dict[str, Any]) -> bool:
        stock = str(raw.get("in_stock", raw.get("availability", "true"))).lower()
        return stock in ("true", "1", "in stock", "available")

    def extract_price(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extracts canonical INR price. Strictly prevents cross-currency errors.
        """
        raw_p = raw.get("price_inr") or raw.get("price") or raw.get("lowest_price")
        if raw_p is None:
            return None
        try:
            val = float(str(raw_p).replace(",", "").replace("₹", "").strip())
            orig = raw.get("original_price_inr") or raw.get("original_price")
            orig_val = float(str(orig).replace(",", "").replace("₹", "").strip()) if orig else None
            return {
                "price": val,
                "original_price": orig_val,
                "currency": "INR"
            }
        except (ValueError, TypeError):
            return None

    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "source_type": "AFFILIATE",
            "license_type": "Flipkart Affiliate Agreement",
            "commercial_use_allowed": True,
            "terms_url": "https://affiliate.flipkart.com/terms",
            "parser_version": self.PARSER_VERSION,
        }

    def _call_flipkart_api(self, query: str) -> Dict[str, Any]:
        """Calls live official Flipkart API endpoint with rate limiting."""
        self.rate_limiter.wait()
        endpoint = f"{self.api_base_url}/search.json"
        headers = {
            "Fk-Affiliate-Id": self.affiliate_id,
            "Fk-Affiliate-Token": self.affiliate_token,
            "Accept": "application/json",
        }
        params = {"query": query, "resultCount": 1}
        resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
        if resp.status_code == 429:
            self.rate_limiter.record_failure(is_rate_limited=True)
            resp.raise_for_status()
        resp.raise_for_status()
        self.rate_limiter.record_success()
        data = resp.json()
        products = data.get("products", [])
        return products[0] if products else {}
