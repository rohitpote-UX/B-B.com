"""
Brand Battle — Search Query Normalizer
Normalizes query tokens using brand aliases, abbreviation expansion,
plural/singular normalization, and regional spelling correction.
"""

import re
import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("brandbattle.search.normalizer")

_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")


def _load_json(filename: str) -> Any:
    path = os.path.join(_DICT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_BRAND_ALIASES: Dict[str, str] = _load_json("brand_aliases.json") or {}
_ABBREVIATIONS: Dict[str, str] = _load_json("abbreviations.json") or {}

# Regional spelling normalization
_REGIONAL_SPELLINGS: Dict[str, str] = {
    "colour": "color",
    "colours": "colors",
    "grey": "gray",
    "aluminium": "aluminum",
    "favourite": "favorite",
    "favourites": "favorites",
    "defence": "defense",
    "centre": "center",
    "fibre": "fiber",
    "metre": "meter",
    "tyre": "tire",
    "catalogue": "catalog",
    "programme": "program",
    "analyse": "analyze",
    "organise": "organize",
    "recognise": "recognize",
    "specialise": "specialize",
}

# Common plural → singular normalization (simple rules)
_IRREGULAR_PLURALS: Dict[str, str] = {
    "mice": "mouse",
    "men": "man",
    "women": "woman",
    "children": "child",
    "feet": "foot",
    "teeth": "tooth",
    "geese": "goose",
    "knives": "knife",
    "shelves": "shelf",
    "leaves": "leaf",
    "scarves": "scarf",
    "glasses": "glass",
    "watches": "watch",
    "boxes": "box",
    "brushes": "brush",
    "dishes": "dish",
    "dresses": "dress",
}

# Unit normalization
_UNIT_MAP: Dict[str, str] = {
    "gb": "GB",
    "tb": "TB",
    "mb": "MB",
    "mah": "mAh",
    "mp": "MP",
    "hz": "Hz",
    "ghz": "GHz",
    "mhz": "MHz",
    "w": "W",
    "kg": "kg",
    "gm": "g",
    "gms": "g",
    "mm": "mm",
    "cm": "cm",
    "inch": "in",
    "inches": "in",
}


class QueryNormalizer:
    """Normalizes query tokens for consistent search matching."""

    def normalize(self, tokens: List[str]) -> List[str]:
        """Normalize a list of tokens and return cleaned tokens."""
        normalized = []
        for token in tokens:
            t = token.lower().strip()
            if not t:
                continue

            # 1. Brand alias resolution
            if t in _BRAND_ALIASES:
                normalized.append(_BRAND_ALIASES[t])
                continue

            # 2. Regional spelling normalization
            if t in _REGIONAL_SPELLINGS:
                t = _REGIONAL_SPELLINGS[t]

            # 3. Unit normalization (standalone units)
            if t in _UNIT_MAP:
                normalized.append(_UNIT_MAP[t])
                continue

            # 4. Number+unit separation: "128gb" → "128 GB"
            unit_match = re.match(r'^(\d+)\s*(gb|tb|mb|mah|mp|hz|ghz|mhz|mm|cm|w|kg)$', t)
            if unit_match:
                normalized.append(unit_match.group(1))
                normalized.append(_UNIT_MAP.get(unit_match.group(2), unit_match.group(2)))
                continue

            # 5. Irregular plural normalization
            if t in _IRREGULAR_PLURALS:
                normalized.append(_IRREGULAR_PLURALS[t])
                continue

            # 6. Simple plural stripping (only for words > 3 chars)
            if len(t) > 3:
                if t.endswith("ies") and len(t) > 4:
                    # batteries → battery
                    normalized.append(t[:-3] + "y")
                    continue
                elif t.endswith("ves") and len(t) > 4:
                    # knives → knife (already handled by irregular)
                    normalized.append(t[:-3] + "f")
                    continue
                elif t.endswith("es") and len(t) > 4 and t[-3] in "sxz":
                    # boxes → box
                    normalized.append(t[:-2])
                    continue
                elif t.endswith("s") and not t.endswith("ss") and not t.endswith("us"):
                    normalized.append(t[:-1])
                    continue

            normalized.append(t)

        return normalized

    def normalize_query_string(self, query: str) -> str:
        """Normalize a full query string and return rejoined."""
        tokens = query.lower().split()
        normalized = self.normalize(tokens)
        return " ".join(normalized)


# Singleton
query_normalizer = QueryNormalizer()
