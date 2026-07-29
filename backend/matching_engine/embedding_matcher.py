"""
Brand Battle - Semantic Embedding Matcher Module
Pluggable vector embedding similarity engine with character/word n-gram TF-IDF vectorizer,
cosine similarity computation, model versioning, and Redis vector caching.
"""

import math
import re
import json
import logging
from typing import Dict, Any, List, Optional
from redis_client import get_cache, set_cache, is_redis_healthy
from matching_engine.matching_config import EMBEDDING_MODEL_VERSION

logger = logging.getLogger("brandbattle.matching.embedding")


class NgramVectorizedEmbeddingProvider:
    """
    Local high-performance n-gram TF-IDF vectorizer embedding provider.
    Computes character and word n-gram term frequencies for zero-latency, offline semantic matching.
    """

    def generate_vector(self, text: str) -> Dict[str, float]:
        """Generates L2-normalized term frequency vector from text."""
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower()).strip()
        words = text_clean.split()

        tf: Dict[str, float] = {}

        # 1. Word unigrams & bigrams
        for i in range(len(words)):
            w = words[i]
            tf[w] = tf.get(w, 0.0) + 1.0
            if i < len(words) - 1:
                bigram = f"{w}_{words[i+1]}"
                tf[bigram] = tf.get(bigram, 0.0) + 1.5

        # 2. Character trigrams for typo resilience
        for w in words:
            if len(w) >= 3:
                for j in range(len(w) - 2):
                    trigram = f"char_{w[j:j+3]}"
                    tf[trigram] = tf.get(trigram, 0.0) + 0.5

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in tf.values()))
        if norm > 0:
            for k in tf:
                tf[k] /= norm

        return tf

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Computes cosine similarity between two normalized sparse term vectors."""
        if not vec1 or not vec2:
            return 0.0

        # Dot product of overlapping keys
        dot_product = 0.0
        # Iterate over smaller dict for speed
        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1

        for term, val1 in vec1.items():
            if term in vec2:
                dot_product += val1 * vec2[term]

        return min(1.0, max(0.0, dot_product))


class EmbeddingMatcher:
    """Pluggable semantic vector embedding similarity engine with caching and fallback."""

    def __init__(self):
        self.provider = NgramVectorizedEmbeddingProvider()
        self.model_version = EMBEDDING_MODEL_VERSION

    def get_cached_vector(self, text: str) -> Dict[str, float]:
        """Gets vector from Redis cache or computes and caches it."""
        cache_key = f"embed:{self.model_version}:{hash(text)}"
        if is_redis_healthy():
            cached = get_cache(cache_key)
            if cached:
                return cached

        vector = self.provider.generate_vector(text)
        if is_redis_healthy():
            set_cache(cache_key, vector, ttl=86400)

        return vector

    def evaluate(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Computes semantic vector embedding similarity between two product representation strings.
        Returns similarity score (0.0 to 1.0) and model version.
        """
        try:
            vec1 = self.get_cached_vector(text1)
            vec2 = self.get_cached_vector(text2)

            sim = self.provider.cosine_similarity(vec1, vec2)
            score = round(sim, 3)

            return {
                "score": score,
                "model_version": self.model_version,
                "explanation": f"Semantic embedding cosine similarity: {score:.3f} ({self.model_version})"
            }
        except Exception as e:
            logger.error(f"EmbeddingMatcher error: {e}")
            return {
                "score": 0.5,
                "model_version": self.model_version,
                "explanation": f"Embedding match fallback due to error: {e}"
            }


embedding_matcher = EmbeddingMatcher()
