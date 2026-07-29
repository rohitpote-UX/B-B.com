"""
Brand Battle - Title Matcher Module
Evaluates title similarity using Jaccard token index, n-gram overlap, and SequenceMatcher.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, Any, List


class TitleMatcher:
    """Evaluates lexical title similarity and token overlap."""

    def evaluate(self, title1: str, title2: str) -> Dict[str, Any]:
        """Calculates title similarity score (0.0 to 1.0) and human-readable explanation."""
        t1_clean = re.sub(r'[^\w\s]', '', title1.lower()).strip()
        t2_clean = re.sub(r'[^\w\s]', '', title2.lower()).strip()

        if not t1_clean or not t2_clean:
            return {"score": 0.0, "explanation": "Empty title"}

        words1 = set(t1_clean.split())
        words2 = set(t2_clean.split())

        # Jaccard index
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0.0

        # Sequence ratio
        seq_ratio = SequenceMatcher(None, t1_clean, t2_clean).ratio()

        score = round((0.6 * jaccard) + (0.4 * seq_ratio), 3)
        explanation = f"Jaccard: {jaccard:.2f}, SeqRatio: {seq_ratio:.2f} ({intersection}/{union} tokens match)"

        return {
            "score": min(1.0, score),
            "jaccard": round(jaccard, 3),
            "seq_ratio": round(seq_ratio, 3),
            "explanation": explanation
        }


title_matcher = TitleMatcher()
