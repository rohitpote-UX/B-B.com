"""
Brand Battle — Admin File Import Catalog Adapter
Second permitted catalog ingestion source.
Enables administrators to import verified CSV and JSON catalog feeds with
complete data provenance, schema mapping, and duplicate prevention.
"""

import os
import csv
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

from catalog_engine.base_adapter import BaseCatalogAdapter
from catalog_engine.schemas import NormalizedProductCandidate
from catalog_engine.normalizer import CatalogNormalizer
from catalog_engine.gtin_validator import GtinValidator
from catalog_engine.security import is_ssrf_safe_url

logger = logging.getLogger("brandbattle.catalog.adapter.admin_import")


class AdminFileImportAdapter(BaseCatalogAdapter):
    """
    Adapter for Admin-provided CSV and JSON catalog files.
    """

    PARSER_VERSION = "admin_import_v1.0"

    def __init__(self, source_id: int = 2, source_name: str = "Admin Catalog Import", file_path: Optional[str] = None):
        super().__init__(source_id=source_id, source_name=source_name, adapter_key="admin_import")
        self.file_path = file_path

    def set_file_path(self, file_path: str):
        self.file_path = file_path

    def discover(self, cursor: Optional[str] = None) -> List[str]:
        if not self.file_path or not os.path.exists(self.file_path):
            return []
        
        ids = []
        records = self._read_file()
        for idx, r in enumerate(records):
            ext_id = r.get("id") or r.get("sku") or r.get("gtin") or f"ADMIN_ROW_{idx+1}"
            ids.append(str(ext_id))
        return ids

    def fetch(self, external_id: str) -> Dict[str, Any]:
        records = self._read_file()
        for idx, r in enumerate(records):
            ext_id = r.get("id") or r.get("sku") or r.get("gtin") or f"ADMIN_ROW_{idx+1}"
            if str(ext_id) == str(external_id):
                return dict(r)
        return {}

    def fetch_batch(self, cursor: Optional[str] = None, limit: int = 50) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        records = self._read_file()
        total = len(records)
        start_idx = int(cursor) if cursor and cursor.isdigit() else 0

        slice_records = records[start_idx : start_idx + limit]
        for idx, r in enumerate(slice_records):
            r["_row_index"] = start_idx + idx

        next_cursor = str(start_idx + limit) if start_idx + limit < total else None
        return slice_records, next_cursor

    def normalize(self, raw_record_id: Optional[int], raw: Dict[str, Any]) -> NormalizedProductCandidate:
        row_idx = raw.get("_row_index", 1)
        ext_id = raw.get("id") or raw.get("sku") or raw.get("gtin") or f"ADMIN_ROW_{row_idx}"
        raw_title = raw.get("name") or raw.get("title") or raw.get("product_name") or ""
        raw_brand = raw.get("brand") or raw.get("manufacturer") or ""
        raw_cat = raw.get("category") or raw.get("category_name") or "Electronics"

        _, canonical_brand = self.map_brand(raw_brand, title_hint=raw_title)
        _, canonical_category = self.map_category(raw_cat, title_hint=raw_title)
        clean_title = CatalogNormalizer.clean_title(raw_title, canonical_brand)

        identifiers = self.extract_identifiers(raw)
        gtin = identifiers.get("gtin")
        is_gtin_valid = False
        if gtin:
            valid, clean_g, _ = GtinValidator.validate(gtin)
            is_gtin_valid = valid
            gtin = clean_g

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
            source_url=raw.get("source_url") or raw.get("url"),
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
            marketplace=raw.get("marketplace") or "BrandBattle Direct",
            seller_name=raw.get("seller_name") or "Authorized Partner",
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
        errors = []
        if not candidate.canonical_brand:
            errors.append("Missing canonical brand")
        if not candidate.clean_title or len(candidate.clean_title) < 3:
            errors.append("Title is missing or less than 3 characters")
        if not candidate.canonical_category:
            errors.append("Missing canonical category")
        if candidate.price is not None and candidate.price < 0:
            errors.append(f"Price cannot be negative: {candidate.price}")
        return len(errors) == 0, errors

    def map_category(self, raw_category: str, title_hint: Optional[str] = None) -> Tuple[str, str]:
        return CatalogNormalizer.normalize_category(raw_category, title_hint)

    def map_brand(self, raw_brand: str, title_hint: Optional[str] = None) -> Tuple[str, str]:
        return CatalogNormalizer.normalize_brand(raw_brand, title_hint)

    def map_variant(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        title = raw.get("name") or raw.get("title") or ""
        attrs = CatalogNormalizer.extract_variant_attributes(title)
        for field in ["color", "storage", "ram", "screen_size"]:
            if raw.get(field):
                attrs[field] = CatalogNormalizer.clean_text(str(raw[field]))
        return attrs

    def extract_identifiers(self, raw: Dict[str, Any]) -> Dict[str, Optional[str]]:
        return {
            "gtin": raw.get("gtin") or raw.get("ean") or raw.get("upc"),
            "ean": raw.get("ean"),
            "upc": raw.get("upc"),
            "mpn": raw.get("mpn"),
            "model_number": raw.get("model_number") or raw.get("model_name"),
            "sku": raw.get("sku"),
        }

    def extract_images(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        images = []
        raw_imgs = raw.get("images") or raw.get("image_url") or raw.get("image")
        if isinstance(raw_imgs, str):
            urls = [u.strip() for u in raw_imgs.split(",") if u.strip()]
            for u in urls:
                if is_ssrf_safe_url(u):
                    images.append({"url": u, "alt_text": raw.get("name", "")})
        elif isinstance(raw_imgs, list):
            for u in raw_imgs:
                if isinstance(u, str) and is_ssrf_safe_url(u):
                    images.append({"url": u.strip(), "alt_text": raw.get("name", "")})
        return images

    def extract_specifications(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        raw_specs = raw.get("specifications") or raw.get("specs")
        specs = {}
        if isinstance(raw_specs, str):
            try:
                specs = json.loads(raw_specs)
            except Exception:
                specs = {}
        elif isinstance(raw_specs, dict):
            specs = raw_specs

        for col in ["ram", "storage", "processor", "battery", "camera", "display", "screen_size"]:
            if raw.get(col):
                specs[col.title()] = CatalogNormalizer.clean_text(str(raw[col]))

        return CatalogNormalizer.clean_specifications(specs)

    def extract_availability(self, raw: Dict[str, Any]) -> bool:
        stock = str(raw.get("availability", raw.get("in_stock", "true"))).lower()
        return stock in ("true", "1", "available", "in stock")

    def extract_price(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raw_p = raw.get("price_inr") or raw.get("price")
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
            "source_type": "ADMIN_IMPORT",
            "license_type": "BrandBattle Authorized Catalog",
            "commercial_use_allowed": True,
            "terms_url": "https://brandbattle.com/terms",
            "parser_version": self.PARSER_VERSION,
        }

    def _read_file(self) -> List[Dict[str, Any]]:
        if not self.file_path or not os.path.exists(self.file_path):
            return []

        if self.file_path.endswith(".csv"):
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                return list(csv.DictReader(f))
        elif self.file_path.endswith(".json"):
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get("products", [])
        return []
