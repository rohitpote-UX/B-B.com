"""
Brand Battle - Enhanced Product Matcher for Knowledge Graph
Multi-signal matching engine that scores candidate MasterProducts using title similarity,
brand matching, model token overlap, specification similarity, and attribute matching.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher
import logging

logger = logging.getLogger("brandbattle.kg.matcher")


class EnhancedMatcher:
    """
    Multi-signal product matching engine.
    Produces a confidence score (0.0–1.0) indicating likelihood that a normalized item
    matches an existing MasterProduct.
    """

    # Configurable match thresholds by category
    CATEGORY_THRESHOLDS = {
        "Smartphones": 0.75,
        "Laptops": 0.70,
        "Headphones": 0.70,
        "Shoes": 0.65,
        "Clothing": 0.60,
        "Watches": 0.70,
        "default": 0.65,
    }

    # Signal weights (must sum to 1.0)
    WEIGHTS = {
        "title_similarity": 0.35,
        "brand_match": 0.20,
        "model_token_overlap": 0.20,
        "spec_similarity": 0.10,
        "attribute_match": 0.15,
    }

    @staticmethod
    def extract_model_tokens(title: str) -> List[str]:
        """Extracts key identifying model tokens from a product title."""
        tokens = []
        # Storage / RAM tokens (e.g., 256GB, 8GB)
        storage_matches = re.findall(r'(?i)\b\d+(?:GB|TB|MB)\b', title)
        tokens.extend([s.upper() for s in storage_matches])

        # Model series tokens (iPhone 17, Galaxy S26, Air Force 1, etc.)
        model_patterns = [
            r'(?i)\b(?:iphone\s*\d+)',
            r'(?i)\b(?:galaxy\s*s\d+(?:\s*ultra)?)',
            r'(?i)\b(?:macbook\s*(?:pro|air)?\s*m\d+)',
            r'(?i)\b(?:air\s*(?:max|force|jordan)\s*\d*)',
            r'(?i)\b(?:ultraboost\s*\w*)',
            r'(?i)\b(?:dunk\s*(?:low|high|mid)?)',
            r'(?i)\b(?:xm\d+)',
            r'(?i)\b(?:quietcomfort\s*\w*)',
            r'(?i)\b(?:g-?shock\s*\w*)',
            r'(?i)\b(?:oneplus\s*\d+)',
            r'(?i)\b(?:pixel\s*\d+)',
        ]

        for pattern in model_patterns:
            matches = re.findall(pattern, title)
            tokens.extend([m.lower().strip() for m in matches])

        return list(set(tokens))

    @staticmethod
    def compute_title_similarity(title1: str, title2: str) -> float:
        """Computes title similarity using Jaccard + SequenceMatcher."""
        t1_clean = re.sub(r'[^\w\s]', '', title1.lower())
        t2_clean = re.sub(r'[^\w\s]', '', title2.lower())

        words1 = set(t1_clean.split())
        words2 = set(t2_clean.split())

        if not words1 or not words2:
            return 0.0

        # Jaccard index
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0.0

        # Sequence ratio
        seq_ratio = SequenceMatcher(None, t1_clean, t2_clean).ratio()

        return (0.6 * jaccard) + (0.4 * seq_ratio)

    @staticmethod
    def compute_brand_match(brand1: str, brand2: str) -> float:
        """Returns 1.0 if brands match, 0.0 otherwise."""
        if not brand1 or not brand2:
            return 0.5  # Unknown brand — neutral score
        return 1.0 if brand1.lower() == brand2.lower() else 0.0

    @staticmethod
    def compute_model_token_overlap(tokens1: List[str], tokens2: List[str]) -> float:
        """Returns overlap ratio between model token sets."""
        if not tokens1 or not tokens2:
            return 0.5  # No tokens — neutral
        s1 = set(t.lower() for t in tokens1)
        s2 = set(t.lower() for t in tokens2)
        overlap = s1.intersection(s2)
        max_len = max(len(s1), len(s2))
        return len(overlap) / max_len if max_len > 0 else 0.0

    @staticmethod
    def compute_spec_similarity(specs1: Dict[str, Any], specs2: Dict[str, Any]) -> float:
        """Compares specifications dictionaries for overlap."""
        if not specs1 or not specs2:
            return 0.5  # No specs — neutral
        all_keys = set(specs1.keys()).union(set(specs2.keys()))
        if not all_keys:
            return 0.5

        matching = 0
        for key in all_keys:
            v1 = str(specs1.get(key, "")).lower().strip()
            v2 = str(specs2.get(key, "")).lower().strip()
            if v1 and v2 and v1 == v2:
                matching += 1
            elif v1 and v2:
                # Partial match for similar values
                sim = SequenceMatcher(None, v1, v2).ratio()
                if sim > 0.8:
                    matching += 0.8

        return matching / len(all_keys) if all_keys else 0.0

    @staticmethod
    def compute_attribute_match(item: Dict[str, Any], master: Dict[str, Any]) -> float:
        """Compares KG attributes (color, material, gender, product_type)."""
        score = 0.0
        comparisons = 0

        attr_pairs = [
            ("kg_color_family", "color_family"),
            ("kg_material", "material"),
            ("kg_gender", "gender"),
            ("kg_product_type", "product_type"),
            ("kg_model_series", "model_series"),
        ]

        for item_key, master_key in attr_pairs:
            iv = item.get(item_key)
            mv = master.get(master_key)
            if iv and mv:
                comparisons += 1
                if str(iv).lower() == str(mv).lower():
                    score += 1.0
            elif iv or mv:
                comparisons += 1  # One side has data, other doesn't — no match

        return score / comparisons if comparisons > 0 else 0.5

    def get_threshold(self, category: str) -> float:
        """Returns match confidence threshold for the given category."""
        return self.CATEGORY_THRESHOLDS.get(category, self.CATEGORY_THRESHOLDS["default"])

    def match_to_master(
        self,
        normalized_item: Dict[str, Any],
        master_candidates: List[Dict[str, Any]],
        db: Session = None,
    ) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Matches a normalized pipeline item against existing MasterProduct candidates.
        Delegates to the Enterprise Hybrid AI Matching Engine.
        """
        try:
            from matching_engine.ensemble_matcher import hybrid_ensemble_matcher
            best_match, confidence, _ = hybrid_ensemble_matcher.match_listing(
                item=normalized_item,
                candidates=master_candidates,
                db=db
            )
            return best_match, confidence
        except Exception as e:
            logger.error(f"Hybrid matcher delegation failed, falling back to rule matcher: {e}")
            title = normalized_item.get("clean_title", "")
            brand = normalized_item.get("canonical_brand", "")
            category = normalized_item.get("canonical_category", "")
            specs = normalized_item.get("normalized_specs", {})
            item_tokens = self.extract_model_tokens(title)

            best_match = None
            highest_confidence = 0.0

            for candidate in master_candidates:
                cand_name = candidate.get("canonical_name", "")
                cand_brand = candidate.get("brand_name", "")

                brand_score = self.compute_brand_match(brand, cand_brand)
                if brand_score == 0.0:
                    continue

                title_sim = self.compute_title_similarity(title, cand_name)
                cand_tokens = self.extract_model_tokens(cand_name)
                token_overlap = self.compute_model_token_overlap(item_tokens, cand_tokens)
                spec_sim = self.compute_spec_similarity(specs, candidate.get("specifications", {}))
                attr_sim = self.compute_attribute_match(normalized_item, candidate)

                confidence = (
                    self.WEIGHTS["title_similarity"] * title_sim +
                    self.WEIGHTS["brand_match"] * brand_score +
                    self.WEIGHTS["model_token_overlap"] * token_overlap +
                    self.WEIGHTS["spec_similarity"] * spec_sim +
                    self.WEIGHTS["attribute_match"] * attr_sim
                )
                confidence = min(1.0, confidence)

                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_match = candidate

            threshold = self.get_threshold(category)
            if highest_confidence >= threshold and best_match:
                return best_match, highest_confidence

            return None, highest_confidence
