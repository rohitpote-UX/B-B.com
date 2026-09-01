"""
Brand Battle — Enterprise Spell Corrector
Edit-distance based spell correction with brand/category awareness,
"Did You Mean" suggestions, and confidence scoring.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.spell")


class SpellCorrector:
    """Enterprise spell correction engine with product vocabulary awareness."""

    def __init__(self):
        self._vocabulary: Set[str] = set()
        self._brand_vocabulary: Set[str] = set()
        self._loaded = False

    def _ensure_vocabulary(self, db: Session) -> None:
        """Build vocabulary from product names, brands, and categories."""
        if self._loaded:
            return
        try:
            from models import Product, Brand, Category

            # Product name tokens
            products = db.query(Product.name).filter(Product.is_active == True).all()
            for (name,) in products:
                for token in name.lower().split():
                    clean = re.sub(r'[^\w]', '', token)
                    if len(clean) >= 2:
                        self._vocabulary.add(clean)

            # Brand names
            brands = db.query(Brand.name).all()
            for (name,) in brands:
                name_lower = name.lower()
                self._brand_vocabulary.add(name_lower)
                self._vocabulary.add(name_lower)
                for token in name_lower.split():
                    self._vocabulary.add(token)

            # Category names
            categories = db.query(Category.name).all()
            for (name,) in categories:
                for token in name.lower().split():
                    clean = re.sub(r'[^\w]', '', token)
                    if len(clean) >= 2:
                        self._vocabulary.add(clean)

            # Add protected terms
            for term in search_config.spell_correction.protected_terms:
                self._vocabulary.add(term.lower())
                self._brand_vocabulary.add(term.lower())

            self._loaded = True
            logger.debug(f"Spell corrector vocabulary loaded: {len(self._vocabulary)} terms")
        except Exception as e:
            logger.warning(f"Failed to load spell corrector vocabulary: {e}")

    def _edit_distance(self, s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    def _find_closest(self, word: str, max_distance: int = 2) -> Optional[Tuple[str, int]]:
        """Find closest vocabulary match within max edit distance."""
        if word in self._vocabulary:
            return (word, 0)

        best_match = None
        best_dist = max_distance + 1

        for vocab_word in self._vocabulary:
            # Quick length filter
            if abs(len(vocab_word) - len(word)) > max_distance:
                continue

            dist = self._edit_distance(word, vocab_word)
            if dist < best_dist:
                best_dist = dist
                best_match = vocab_word

        if best_match and best_dist <= max_distance:
            return (best_match, best_dist)
        return None

    def correct_query(self, tokens: List[str], db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Correct spelling errors in query tokens.
        Returns corrected tokens, corrections made, and did-you-mean suggestions.
        """
        if db:
            self._ensure_vocabulary(db)

        if not self._vocabulary:
            return {
                "corrected_tokens": tokens,
                "corrections": [],
                "did_you_mean": None,
                "was_corrected": False,
            }

        corrected = []
        corrections = []
        max_dist = search_config.spell_correction.max_edit_distance
        min_len = search_config.spell_correction.min_word_length

        for token in tokens:
            t_lower = token.lower()

            # Skip short tokens, numbers, and protected terms
            if (
                len(t_lower) < min_len
                or re.match(r'^\d+$', t_lower)
                or t_lower in self._brand_vocabulary
            ):
                corrected.append(t_lower)
                continue

            # Already in vocabulary
            if t_lower in self._vocabulary:
                corrected.append(t_lower)
                continue

            # Try to find closest match
            match = self._find_closest(t_lower, max_dist)
            if match:
                corrected_word, distance = match
                confidence = 1.0 - (distance / max(len(t_lower), 1))

                if confidence >= search_config.spell_correction.min_confidence:
                    corrected.append(corrected_word)
                    corrections.append({
                        "original": t_lower,
                        "corrected": corrected_word,
                        "distance": distance,
                        "confidence": round(confidence, 2),
                    })
                else:
                    corrected.append(t_lower)  # Keep original if low confidence
            else:
                corrected.append(t_lower)

        was_corrected = len(corrections) > 0
        did_you_mean = " ".join(corrected) if was_corrected else None

        return {
            "corrected_tokens": corrected,
            "corrections": corrections,
            "did_you_mean": did_you_mean,
            "was_corrected": was_corrected,
        }


# Singleton
spell_corrector = SpellCorrector()
