"""
Brand Battle - AI Product Matching & Deduplication Engine
Extracts model tokens and evaluates semantic/fuzzy title similarity to link marketplace offers to canonical master products.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher
import logging

logger = logging.getLogger("brandbattle.matcher")


class AIProductMatcher:
    """Intelligent entity resolution engine matching multi-platform offers to master products."""

    @staticmethod
    def extract_model_tokens(title: str) -> List[str]:
        """Extracts key identifying model tokens (e.g. 'iPhone 17', 'S25 Ultra', 'Air Force 1', '256GB')."""
        tokens = []
        # Storage / RAM tokens
        storage_matches = re.findall(r'(?i)\b\d+(?:GB|TB)\b', title)
        tokens.extend([s.upper() for s in storage_matches])

        # Model series tokens (e.g. S24, S25, iPhone 15, iPhone 16, iPhone 17, M3, M4)
        model_matches = re.findall(r'(?i)\b(?:iphone\s*\d+|s\d+\s*ultra|galaxy\s*s\d+|macbook\s*(?:pro|air)?\s*m\d+)\b', title)
        tokens.extend([m.lower() for m in model_matches])

        return list(set(tokens))

    @staticmethod
    def compute_similarity(title1: str, title2: str) -> float:
        """Computes similarity score between two product titles using token Jaccard + SequenceMatcher."""
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

        # Weighted combination
        return (0.6 * jaccard) + (0.4 * seq_ratio)

    def match_product(
        self, normalized_item: Dict[str, Any], existing_products: List[Dict[str, Any]]
    ) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Matches normalized item against database of existing master products.
        Returns: (matched_master_product: Dict or None, confidence_score: float)
        """
        title = normalized_item.get("clean_title", "")
        brand = normalized_item.get("canonical_brand", "")
        item_tokens = set(self.extract_model_tokens(title))

        best_match = None
        highest_confidence = 0.0

        for candidate in existing_products:
            cand_title = candidate.get("name", "")
            cand_brand = candidate.get("brand", {}).get("name") if isinstance(candidate.get("brand"), dict) else candidate.get("brand", "")

            # Brand must match if known
            if brand and cand_brand and brand.lower() != str(cand_brand).lower():
                continue

            cand_tokens = set(self.extract_model_tokens(cand_title))

            # Base string similarity
            sim_score = self.compute_similarity(title, cand_title)

            # Token overlap bonus
            token_bonus = 0.0
            if item_tokens and cand_tokens:
                overlap = item_tokens.intersection(cand_tokens)
                if overlap:
                    token_bonus = 0.25 * (len(overlap) / max(len(item_tokens), len(cand_tokens)))

            final_confidence = min(1.0, sim_score + token_bonus)

            if final_confidence > highest_confidence:
                highest_confidence = final_confidence
                best_match = candidate

        # Threshold check: >= 0.70 confidence counts as a valid match
        if highest_confidence >= 0.70 and best_match:
            logger.info(f"Matched '{title}' -> Master ID {best_match.get('id')} ({best_match.get('name')}) [Conf: {highest_confidence:.2f}]")
            return best_match, highest_confidence

        logger.info(f"No existing master product match for '{title}' [Highest conf: {highest_confidence:.2f}]. Creating canonical master.")
        return None, highest_confidence
