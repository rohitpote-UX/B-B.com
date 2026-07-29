"""
Brand Battle - Specification Matcher Module
Structured specification matcher with unit normalization and tolerance rules.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, Any


class SpecificationMatcher:
    """Compares structured specification dictionaries for exact/partial equivalence."""

    def evaluate(self, specs1: Dict[str, Any], specs2: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates specification similarity score (0.0 to 1.0)."""
        if not specs1 or not specs2:
            return {"score": 0.5, "explanation": "One or both specification dictionaries empty"}

        all_keys = set(specs1.keys()).union(set(specs2.keys()))
        if not all_keys:
            return {"score": 0.5, "explanation": "No specification keys found"}

        matching_score = 0.0
        evaluated_keys = 0

        for key in all_keys:
            v1 = specs1.get(key)
            v2 = specs2.get(key)

            if v1 is not None and v2 is not None:
                evaluated_keys += 1
                str1 = str(v1).strip().lower()
                str2 = str(v2).strip().lower()

                if str1 == str2:
                    matching_score += 1.0
                else:
                    # Partial unit similarity (e.g. "256 GB" vs "256GB")
                    clean1 = re.sub(r'\s+', '', str1)
                    clean2 = re.sub(r'\s+', '', str2)
                    if clean1 == clean2:
                        matching_score += 1.0
                    else:
                        sim = SequenceMatcher(None, str1, str2).ratio()
                        if sim >= 0.8:
                            matching_score += sim

        if evaluated_keys == 0:
            return {"score": 0.5, "explanation": "No overlapping specification keys"}

        final_score = round(matching_score / evaluated_keys, 3)
        return {
            "score": final_score,
            "evaluated_keys": evaluated_keys,
            "explanation": f"Spec match: {final_score:.2f} across {evaluated_keys} keys"
        }


specification_matcher = SpecificationMatcher()
