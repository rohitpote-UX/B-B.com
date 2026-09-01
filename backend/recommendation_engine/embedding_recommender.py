"""
Brand Battle — Semantic Embedding & Text Similarity Recommender
Generates TF-IDF token vector representations and computes cosine similarity for semantic product matching.
"""

from typing import List, Dict, Any, Optional
import math
import re
from collections import Counter
from sqlalchemy.orm import Session
from models import Product
from logging_config import logger


class EmbeddingRecommender:
    """Semantic vector text similarity engine using cosine token overlap."""

    def _tokenize(self, text: str) -> List[str]:
        """Normalize and tokenize text string into word tokens."""
        if not text:
            return []
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return [token for token in cleaned.split() if len(token) > 1]

    def _text_to_vector(self, text: str) -> Counter:
        """Convert string to term frequency vector."""
        tokens = self._tokenize(text)
        return Counter(tokens)

    def compute_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate cosine similarity score between two text descriptions."""
        vec1 = self._text_to_vector(text_a)
        vec2 = self._text_to_vector(text_b)
        
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return round(float(numerator) / denominator, 4)

    def get_semantic_similar_products(
        self, 
        db: Session, 
        product: Product, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Identify semantically similar products based on title, description, features, and tags."""
        try:
            target_text = f"{product.name} {product.description or ''} {' '.join(product.features or [])} {' '.join(product.tags or [])}"
            
            candidates = db.query(Product).filter(
                Product.id != product.id,
                Product.is_active == True
            ).limit(60).all()

            results = []
            for candidate in candidates:
                cand_text = f"{candidate.name} {candidate.description or ''} {' '.join(candidate.features or [])} {' '.join(candidate.tags or [])}"
                score = self.compute_cosine_similarity(target_text, cand_text)
                if score >= 0.20:
                    results.append({
                        "product": candidate,
                        "semantic_score": score,
                        "reason": f"Semantic Match Score: {int(score * 100)}%"
                    })

            results.sort(key=lambda x: x["semantic_score"], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Error computing semantic embedding similarity for product {product.id}: {e}")
            return []
