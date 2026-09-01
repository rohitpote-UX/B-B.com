"""
Brand Battle — Semantic Search Engine
Embedding-based similarity retrieval using the existing NgramVectorizedEmbeddingProvider.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload

from models import Product
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.semantic")

# Reuse the matching engine's embedding provider
try:
    from matching_engine.embedding_matcher import NgramVectorizedEmbeddingProvider
    _embedding_provider = NgramVectorizedEmbeddingProvider()
except ImportError:
    _embedding_provider = None
    logger.warning("Embedding provider not available — semantic search disabled")


class SemanticSearch:
    """Embedding cosine similarity search over product text representations."""

    def __init__(self):
        self.provider = _embedding_provider

    def search(
        self,
        query: str,
        candidate_ids: List[int],
        db: Session,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Compute semantic similarity between query and candidate products.
        Returns scored results sorted by cosine similarity.
        """
        if not self.provider or not search_config.enable_semantic_search:
            return []

        if not query.strip():
            return []

        # Generate query vector
        query_vector = self.provider.generate_vector(query)
        if not query_vector:
            return []

        # Load candidate products
        q = db.query(Product).filter(
            Product.is_active == True
        ).options(joinedload(Product.brand), joinedload(Product.category))

        if candidate_ids:
            q = q.filter(Product.id.in_(candidate_ids))

        products = q.limit(limit * 2).all()  # Fetch extra, then sort and trim

        results = []
        for product in products:
            # Build product text representation
            product_text = self._build_product_text(product)
            if not product_text:
                continue

            product_vector = self.provider.generate_vector(product_text)
            similarity = self.provider.cosine_similarity(query_vector, product_vector)

            if similarity > 0.05:  # Minimum threshold to include
                results.append({
                    "product": product,
                    "semantic_score": round(similarity, 4),
                    "source": "semantic_search",
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x["semantic_score"], reverse=True)

        return results[:limit]

    def _build_product_text(self, product: Product) -> str:
        """Build a rich text representation of a product for embedding."""
        parts = []

        if product.name:
            parts.append(product.name)
        if product.brand and product.brand.name:
            parts.append(product.brand.name)
        if product.category and product.category.name:
            parts.append(product.category.name)
        if product.short_description:
            parts.append(product.short_description)
        if product.tags:
            parts.extend(product.tags[:10])
        if product.features:
            parts.extend(product.features[:5])

        # Include spec keys (not values, to keep vector semantic)
        if product.specifications and isinstance(product.specifications, dict):
            parts.extend(list(product.specifications.keys())[:10])

        return " ".join(parts)


# Singleton
semantic_search = SemanticSearch()
