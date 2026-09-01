"""
Brand Battle — Knowledge Graph Search Engine
PKG graph-traversal retrieval using MasterProduct relationships, attributes, and tags.
"""

import logging
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from models import (
    Product, MasterProduct, ProductRelationship, ProductAttribute,
    ProductTag, SearchMetadata
)
from search_platform.query_parser import ParsedQuery
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.kg")


class KnowledgeGraphSearch:
    """Retrieves products via PKG graph traversal, attribute matching, and tag search."""

    def search(
        self,
        parsed: ParsedQuery,
        candidate_ids: List[int],
        db: Session,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Search the Product Knowledge Graph for matching products.
        Uses structured attributes, tags, and relationship edges.
        """
        if not search_config.enable_kg_search:
            return []

        results: Dict[int, Dict[str, Any]] = {}

        # 1. Attribute-based KG search
        self._search_attributes(parsed, candidate_ids, db, results)

        # 2. Tag-based KG search
        self._search_tags(parsed, candidate_ids, db, results)

        # 3. SearchMetadata-boosted products
        self._search_metadata_boost(candidate_ids, db, results)

        # Resolve product objects
        product_ids = list(results.keys())[:limit]
        if not product_ids:
            return []

        products = (
            db.query(Product)
            .filter(Product.id.in_(product_ids), Product.is_active == True)
            .options(joinedload(Product.brand), joinedload(Product.category))
            .all()
        )
        product_map = {p.id: p for p in products}

        final_results = []
        for pid, score_data in results.items():
            product = product_map.get(pid)
            if product:
                final_results.append({
                    "product": product,
                    "kg_score": score_data.get("score", 0.0),
                    "source": "knowledge_graph_search",
                    "kg_signals": score_data.get("signals", []),
                })

        final_results.sort(key=lambda x: x["kg_score"], reverse=True)
        return final_results[:limit]

    def _search_attributes(
        self, parsed: ParsedQuery, candidate_ids: List[int],
        db: Session, results: Dict[int, Dict[str, Any]]
    ) -> None:
        """Search ProductAttribute table for structured matches."""
        search_terms: List[tuple] = []

        if parsed.color:
            search_terms.append(("color", parsed.color))
            search_terms.append(("colour", parsed.color))
        if parsed.material:
            search_terms.append(("material", parsed.material))
        if parsed.gender:
            search_terms.append(("gender", parsed.gender))

        # Search remaining keywords as potential attribute values
        for kw in parsed.remaining_keywords[:3]:
            search_terms.append((None, kw))

        if not search_terms:
            return

        for attr_name, attr_value in search_terms:
            q = db.query(ProductAttribute.master_product_id)
            if attr_name:
                q = q.filter(
                    ProductAttribute.attribute_name.ilike(attr_name),
                    ProductAttribute.attribute_value.ilike(f"%{attr_value}%"),
                    ProductAttribute.is_searchable == True,
                )
            else:
                q = q.filter(
                    ProductAttribute.attribute_value.ilike(f"%{attr_value}%"),
                    ProductAttribute.is_searchable == True,
                )

            master_ids = [row[0] for row in q.limit(100).all()]
            if master_ids:
                # Map master_product_id to product_id
                prods = (
                    db.query(Product.id)
                    .filter(Product.master_product_id.in_(master_ids), Product.is_active == True)
                    .all()
                )
                for (pid,) in prods:
                    if candidate_ids and pid not in candidate_ids:
                        continue
                    if pid not in results:
                        results[pid] = {"score": 0.0, "signals": []}
                    results[pid]["score"] += 0.15
                    results[pid]["signals"].append(f"attribute:{attr_name or 'keyword'}={attr_value}")

    def _search_tags(
        self, parsed: ParsedQuery, candidate_ids: List[int],
        db: Session, results: Dict[int, Dict[str, Any]]
    ) -> None:
        """Search ProductTag table for tag-based matches."""
        search_tags = list(parsed.remaining_keywords[:5])
        if parsed.product_type:
            search_tags.append(parsed.product_type)
        if parsed.color:
            search_tags.append(parsed.color)

        if not search_tags:
            return

        tag_filters = [ProductTag.tag.ilike(f"%{t}%") for t in search_tags]
        tag_results = (
            db.query(ProductTag.master_product_id)
            .filter(or_(*tag_filters))
            .limit(200)
            .all()
        )

        master_ids = list(set(row[0] for row in tag_results))
        if master_ids:
            prods = (
                db.query(Product.id)
                .filter(Product.master_product_id.in_(master_ids), Product.is_active == True)
                .all()
            )
            for (pid,) in prods:
                if candidate_ids and pid not in candidate_ids:
                    continue
                if pid not in results:
                    results[pid] = {"score": 0.0, "signals": []}
                results[pid]["score"] += 0.10
                results[pid]["signals"].append("tag_match")

    def _search_metadata_boost(
        self, candidate_ids: List[int],
        db: Session, results: Dict[int, Dict[str, Any]]
    ) -> None:
        """Apply SearchMetadata boost scores to existing candidates."""
        if not candidate_ids:
            return

        # Get products with master_product_id
        products_with_masters = (
            db.query(Product.id, Product.master_product_id)
            .filter(Product.id.in_(candidate_ids), Product.master_product_id != None)
            .all()
        )

        master_to_product = {row[1]: row[0] for row in products_with_masters}
        master_ids = list(master_to_product.keys())

        if not master_ids:
            return

        metadata_entries = (
            db.query(SearchMetadata)
            .filter(SearchMetadata.master_product_id.in_(master_ids))
            .all()
        )

        for meta in metadata_entries:
            pid = master_to_product.get(meta.master_product_id)
            if pid is None:
                continue

            boost = (meta.boost_score or 1.0) * 0.05
            trending = (meta.trending_score or 0.0) * 0.03
            popularity = (meta.popularity_score or 0.0) * 0.03

            if pid not in results:
                results[pid] = {"score": 0.0, "signals": []}
            results[pid]["score"] += boost + trending + popularity
            if boost > 0.05:
                results[pid]["signals"].append(f"search_boost:{meta.boost_score}")


# Singleton
knowledge_graph_search = KnowledgeGraphSearch()
