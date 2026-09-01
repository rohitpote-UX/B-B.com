"""
Brand Battle — Search Query Parser
Parses raw query text into a structured ParsedQuery with extracted brand, category,
color, material, gender, product type, price constraints, and remaining keywords.
"""

import re
import json
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.parser")

# Load dictionaries
_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")

def _load_json(filename: str) -> Any:
    path = os.path.join(_DICT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

_STOP_WORDS = set(_load_json("stop_words.json") or [])
_BRAND_ALIASES = _load_json("brand_aliases.json") or {}

# Import color/material/gender/product type maps from KG normalizer (read-only reuse)
try:
    from knowledge_graph.normalizer_enhanced import (
        COLOR_FAMILY_MAP, MATERIAL_MAP, GENDER_KEYWORDS, PRODUCT_TYPE_MAP
    )
except ImportError:
    COLOR_FAMILY_MAP = {}
    MATERIAL_MAP = {}
    GENDER_KEYWORDS = {}
    PRODUCT_TYPE_MAP = {}


@dataclass
class ParsedQuery:
    """Canonical structured representation of a search query."""
    raw_query: str = ""
    cleaned_query: str = ""
    brand: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    gender: Optional[str] = None
    product_type: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    intent_keywords: List[str] = field(default_factory=list)
    remaining_keywords: List[str] = field(default_factory=list)
    is_comparison: bool = False
    is_question: bool = False
    is_deal_search: bool = False
    has_superlative: bool = False
    tokens: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "cleaned_query": self.cleaned_query,
            "brand": self.brand,
            "category": self.category,
            "color": self.color,
            "material": self.material,
            "gender": self.gender,
            "product_type": self.product_type,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "intent_keywords": self.intent_keywords,
            "remaining_keywords": self.remaining_keywords,
            "is_comparison": self.is_comparison,
            "is_question": self.is_question,
            "is_deal_search": self.is_deal_search,
            "has_superlative": self.has_superlative,
        }


class QueryParser:
    """Parses raw user queries into structured ParsedQuery representations."""

    def __init__(self):
        self._brand_names: List[str] = []
        self._category_names: List[str] = []
        self._brands_loaded = False

    def _ensure_vocabulary(self, db: Session) -> None:
        """Lazy-load brand and category names from DB (cached in memory)."""
        if self._brands_loaded:
            return
        try:
            from models import Brand, Category
            brands = db.query(Brand.name).all()
            self._brand_names = sorted(
                [b.name.lower() for b in brands], key=len, reverse=True
            )
            categories = db.query(Category.name).all()
            self._category_names = sorted(
                [c.name.lower() for c in categories], key=len, reverse=True
            )
            self._brands_loaded = True
        except Exception as e:
            logger.warning(f"Could not load brand/category vocabulary: {e}")

    def parse(self, raw_query: str, db: Optional[Session] = None) -> ParsedQuery:
        """Parse a raw search query into a structured ParsedQuery."""
        result = ParsedQuery(raw_query=raw_query)

        if not raw_query or not raw_query.strip():
            return result

        # 1. Clean the query
        cleaned = re.sub(r'[^\w\s₹$€£¥,./-]', ' ', raw_query).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        result.cleaned_query = cleaned
        query_lower = cleaned.lower()
        tokens = query_lower.split()
        result.tokens = list(tokens)

        # 2. Load vocabulary if DB available
        if db:
            self._ensure_vocabulary(db)

        # 3. Extract price constraints
        self._extract_prices(query_lower, result)

        # 4. Detect comparison intent
        for kw in search_config.parser.comparison_keywords:
            if kw in tokens:
                result.is_comparison = True
                result.intent_keywords.append(kw)
                break

        # 5. Detect question intent
        for kw in search_config.parser.question_keywords:
            if kw in tokens:
                result.is_question = True
                result.intent_keywords.append(kw)
                break

        # 6. Detect deal intent
        for kw in search_config.parser.deal_keywords:
            if kw in tokens:
                result.is_deal_search = True
                result.intent_keywords.append(kw)
                break

        # 7. Detect superlatives
        for kw in search_config.parser.superlative_keywords:
            if kw in tokens:
                result.has_superlative = True
                result.intent_keywords.append(kw)
                break

        # 8. Extract brand (longest match first from DB vocabulary)
        self._extract_brand(query_lower, result)

        # 9. Extract category
        self._extract_category(query_lower, result)

        # 10. Extract color
        for token in tokens:
            normalized_color = COLOR_FAMILY_MAP.get(token)
            if normalized_color:
                result.color = normalized_color
                break
        # Also check bigrams for color
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            normalized_color = COLOR_FAMILY_MAP.get(bigram)
            if normalized_color:
                result.color = normalized_color
                break

        # 11. Extract material
        for token in tokens:
            normalized_mat = MATERIAL_MAP.get(token)
            if normalized_mat:
                result.material = normalized_mat
                break

        # 12. Extract gender
        for token in tokens:
            normalized_gender = GENDER_KEYWORDS.get(token)
            if normalized_gender:
                result.gender = normalized_gender
                break

        # 13. Extract product type (check bigrams first, then unigrams)
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            ptype = PRODUCT_TYPE_MAP.get(bigram)
            if ptype:
                result.product_type = ptype
                break
        if not result.product_type:
            for token in tokens:
                ptype = PRODUCT_TYPE_MAP.get(token)
                if ptype:
                    result.product_type = ptype
                    break

        # 14. Build remaining keywords (tokens not already extracted)
        extracted_lower = set()
        if result.brand:
            extracted_lower.update(result.brand.lower().split())
        if result.category:
            extracted_lower.update(result.category.lower().split())
        if result.color:
            extracted_lower.add(result.color)
        if result.material:
            extracted_lower.add(result.material)
        if result.gender:
            extracted_lower.add(result.gender)

        result.remaining_keywords = [
            t for t in tokens
            if t not in _STOP_WORDS
            and t not in extracted_lower
            and t not in result.intent_keywords
            and not re.match(r'^[\d₹$€£¥,.]+$', t)
        ]

        return result

    def _extract_prices(self, query_lower: str, result: ParsedQuery) -> None:
        """Extract price constraints from the query."""
        # Pattern: "under/below/less than ₹5000" or "under 5000"
        under_match = re.search(
            r'(?:under|below|less\s+than|upto|up\s+to|max|maximum)\s*[₹$€£¥]?\s*(\d[\d,]*\.?\d*)',
            query_lower
        )
        if under_match:
            result.price_max = float(under_match.group(1).replace(',', ''))

        # Pattern: "above/over/more than/min/starting ₹5000"
        over_match = re.search(
            r'(?:above|over|more\s+than|min|minimum|starting|from)\s*[₹$€£¥]?\s*(\d[\d,]*\.?\d*)',
            query_lower
        )
        if over_match:
            result.price_min = float(over_match.group(1).replace(',', ''))

        # Pattern: "between 5000 and 10000" or "5000-10000" or "5000 to 10000"
        range_match = re.search(
            r'(?:between\s+)?[₹$€£¥]?\s*(\d[\d,]*\.?\d*)\s*(?:to|-|and)\s*[₹$€£¥]?\s*(\d[\d,]*\.?\d*)',
            query_lower
        )
        if range_match and not under_match and not over_match:
            result.price_min = float(range_match.group(1).replace(',', ''))
            result.price_max = float(range_match.group(2).replace(',', ''))

        # Standalone number at end: "nike shoes 5000" → treat as price_max
        if result.price_max is None and result.price_min is None:
            standalone = re.search(r'\b(\d{3,7})\s*$', query_lower)
            if standalone:
                val = float(standalone.group(1))
                if val >= 100:  # Likely a price, not a model number like "270"
                    result.price_max = val

    def _extract_brand(self, query_lower: str, result: ParsedQuery) -> None:
        """Extract brand from query using DB vocabulary and alias dictionary."""
        # 1. Check brand aliases first
        for alias, canonical in _BRAND_ALIASES.items():
            if alias in query_lower:
                result.brand = canonical
                return

        # 2. Check DB brand names (longest match first)
        for brand_name in self._brand_names:
            if brand_name in query_lower:
                result.brand = brand_name
                return

    def _extract_category(self, query_lower: str, result: ParsedQuery) -> None:
        """Extract category from query using DB vocabulary."""
        for cat_name in self._category_names:
            if cat_name in query_lower:
                result.category = cat_name
                return


# Singleton
query_parser = QueryParser()
