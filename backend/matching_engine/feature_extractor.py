"""
Brand Battle - Feature Extractor
Extracts structured identity signals (brand, model, series, color, material, gender,
specs, normalized tokens) from listing payloads for matching modules.
"""

import re
from typing import Dict, Any, List, Optional
from knowledge_graph.normalizer_enhanced import EnhancedNormalizer

_normalizer = EnhancedNormalizer()


class FeatureExtractor:
    """Extracts structured identity signals for multi-signal matching evaluation."""

    def extract_features(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts complete normalized feature dictionary from a raw/normalized item."""
        # Run enhanced normalizer if not already run
        enhanced = _normalizer.enhance_normalized_item(dict(item))

        title = enhanced.get("clean_title", enhanced.get("raw_title", ""))
        brand = enhanced.get("canonical_brand", enhanced.get("brand_hint", ""))
        category = enhanced.get("canonical_category", enhanced.get("category_hint", ""))
        specs = enhanced.get("normalized_specs", enhanced.get("specifications", {}))

        tokens = self.extract_normalized_tokens(title)

        return {
            "clean_title": title,
            "raw_title": enhanced.get("raw_title", title),
            "brand": brand,
            "category": category,
            "subcategory": enhanced.get("kg_subcategory"),
            "product_type": enhanced.get("kg_product_type"),
            "model_series": enhanced.get("kg_model_series"),
            "model_name": enhanced.get("kg_model_name"),
            "variant": enhanced.get("kg_variant"),
            "color_family": enhanced.get("kg_color_family"),
            "material": enhanced.get("kg_material"),
            "gender": enhanced.get("kg_gender"),
            "specs": specs,
            "price": enhanced.get("price", 0.0),
            "marketplace": enhanced.get("marketplace", ""),
            "normalized_tokens": tokens,
        }

    def extract_normalized_tokens(self, text: str) -> List[str]:
        """Cleans and tokenizes text into lowercase normalized alphanumeric tokens."""
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        stopwords = {"with", "for", "and", "in", "by", "the", "of", "a", "an", "edition", "series", "pro", "max"}
        tokens = [w.strip() for w in text_clean.split() if len(w.strip()) > 1 and w.strip() not in stopwords]
        return list(set(tokens))


feature_extractor = FeatureExtractor()
