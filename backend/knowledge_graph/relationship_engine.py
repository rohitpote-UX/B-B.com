"""
Brand Battle - Product Relationship Engine
Automatically detects and creates typed relationships between MasterProducts
based on shared attributes, category, brand, and product hierarchy.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

import models
from models import RelationshipType

logger = logging.getLogger("brandbattle.kg.relationships")


class RelationshipEngine:
    """Automatically discovers and manages relationships between MasterProducts."""

    def detect_relationships(self, master_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Analyzes a MasterProduct and auto-detects relationships with other masters.
        Returns list of created relationships.
        """
        master = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
        if not master:
            return []

        created = []

        # 1. Same Brand relationships
        if master.brand_id:
            same_brand = (
                db.query(models.MasterProduct)
                .filter(
                    models.MasterProduct.brand_id == master.brand_id,
                    models.MasterProduct.id != master.id,
                    models.MasterProduct.is_active == True,
                )
                .limit(20)
                .all()
            )
            for other in same_brand:
                rel = self._create_relationship_if_new(
                    db, master.id, other.id,
                    RelationshipType.SAME_BRAND,
                    confidence=0.9,
                    bidirectional=True,
                    metadata={"reason": "Same brand"}
                )
                if rel:
                    created.append(rel)

        # 2. Similar Style (same category + same product_type + different brand)
        if master.category_id and master.product_type:
            similar = (
                db.query(models.MasterProduct)
                .filter(
                    models.MasterProduct.category_id == master.category_id,
                    models.MasterProduct.product_type == master.product_type,
                    models.MasterProduct.id != master.id,
                    models.MasterProduct.brand_id != master.brand_id,
                    models.MasterProduct.is_active == True,
                )
                .limit(10)
                .all()
            )
            for other in similar:
                rel = self._create_relationship_if_new(
                    db, master.id, other.id,
                    RelationshipType.SIMILAR_STYLE,
                    confidence=0.7,
                    bidirectional=True,
                    metadata={"reason": f"Same category ({master.product_type})"}
                )
                if rel:
                    created.append(rel)

        # 3. Frequently Compared (same model series + different brand)
        if master.model_series and master.category_id:
            comparable = (
                db.query(models.MasterProduct)
                .filter(
                    models.MasterProduct.category_id == master.category_id,
                    models.MasterProduct.id != master.id,
                    models.MasterProduct.brand_id != master.brand_id,
                    models.MasterProduct.is_active == True,
                )
                .limit(5)
                .all()
            )
            for other in comparable:
                # Only if they share a product_type
                if other.product_type and master.product_type and other.product_type == master.product_type:
                    price_diff = 0
                    if master.lowest_price and other.lowest_price:
                        price_diff = abs(master.lowest_price - other.lowest_price) / max(master.lowest_price, other.lowest_price, 1)

                    # If within 50% price range, they're likely frequently compared
                    if price_diff < 0.5:
                        rel = self._create_relationship_if_new(
                            db, master.id, other.id,
                            RelationshipType.FREQUENTLY_COMPARED,
                            confidence=0.6 + (0.3 * (1 - price_diff)),  # Higher confidence if closer price
                            bidirectional=True,
                            metadata={"reason": "Same type, similar price range", "price_diff_pct": round(price_diff * 100, 1)}
                        )
                        if rel:
                            created.append(rel)

        # 4. Alternative (same category + same price range + different brand)
        if master.category_id and master.lowest_price:
            price_low = master.lowest_price * 0.7
            price_high = master.lowest_price * 1.3
            alternatives = (
                db.query(models.MasterProduct)
                .filter(
                    models.MasterProduct.category_id == master.category_id,
                    models.MasterProduct.id != master.id,
                    models.MasterProduct.brand_id != master.brand_id,
                    models.MasterProduct.lowest_price.between(price_low, price_high),
                    models.MasterProduct.is_active == True,
                )
                .limit(5)
                .all()
            )
            for other in alternatives:
                rel = self._create_relationship_if_new(
                    db, master.id, other.id,
                    RelationshipType.ALTERNATIVE,
                    confidence=0.65,
                    bidirectional=True,
                    metadata={"reason": "Same category, similar price"}
                )
                if rel:
                    created.append(rel)

        # 5. Premium/Budget Alternative (same category, significantly different price)
        if master.category_id and master.lowest_price:
            # Premium alternatives: > 50% more expensive
            premium_candidates = (
                db.query(models.MasterProduct)
                .filter(
                    models.MasterProduct.category_id == master.category_id,
                    models.MasterProduct.id != master.id,
                    models.MasterProduct.lowest_price > master.lowest_price * 1.5,
                    models.MasterProduct.is_active == True,
                )
                .limit(3)
                .all()
            )
            for other in premium_candidates:
                rel = self._create_relationship_if_new(
                    db, master.id, other.id,
                    RelationshipType.PREMIUM_ALTERNATIVE,
                    confidence=0.6,
                    bidirectional=False,
                    metadata={"reason": "Same category, higher price tier"}
                )
                if rel:
                    created.append(rel)

            # Budget alternatives: > 50% cheaper
            budget_candidates = (
                db.query(models.MasterProduct)
                .filter(
                    models.MasterProduct.category_id == master.category_id,
                    models.MasterProduct.id != master.id,
                    models.MasterProduct.lowest_price < master.lowest_price * 0.5,
                    models.MasterProduct.is_active == True,
                )
                .limit(3)
                .all()
            )
            for other in budget_candidates:
                rel = self._create_relationship_if_new(
                    db, master.id, other.id,
                    RelationshipType.BUDGET_ALTERNATIVE,
                    confidence=0.6,
                    bidirectional=False,
                    metadata={"reason": "Same category, lower price tier"}
                )
                if rel:
                    created.append(rel)

        logger.info(f"Detected {len(created)} relationships for Master ID {master_id}")
        return created

    def _create_relationship_if_new(
        self,
        db: Session,
        source_id: int,
        target_id: int,
        rel_type: RelationshipType,
        confidence: float = 1.0,
        bidirectional: bool = False,
        metadata: Dict[str, Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """Creates a relationship if it doesn't already exist."""
        # Check existing
        existing = (
            db.query(models.ProductRelationship)
            .filter(
                models.ProductRelationship.source_master_id == source_id,
                models.ProductRelationship.target_master_id == target_id,
                models.ProductRelationship.relationship_type == rel_type.value,
            )
            .first()
        )
        if existing:
            return None

        # Also check reverse for bidirectional
        if bidirectional:
            existing_reverse = (
                db.query(models.ProductRelationship)
                .filter(
                    models.ProductRelationship.source_master_id == target_id,
                    models.ProductRelationship.target_master_id == source_id,
                    models.ProductRelationship.relationship_type == rel_type.value,
                )
                .first()
            )
            if existing_reverse:
                return None

        # Calculate signal breakdown and weighted score
        brand_score = 1.0 if rel_type == RelationshipType.SAME_BRAND else (0.8 if metadata and "Same brand" in str(metadata) else 0.0)
        category_score = 1.0 if rel_type in [RelationshipType.SIMILAR_STYLE, RelationshipType.ALTERNATIVE, RelationshipType.FREQUENTLY_COMPARED] else 0.5
        price_score = 0.9 if rel_type == RelationshipType.ALTERNATIVE else (0.7 if rel_type in [RelationshipType.PREMIUM_ALTERNATIVE, RelationshipType.BUDGET_ALTERNATIVE] else 0.5)

        signal_breakdown = {
            "brand_similarity": brand_score,
            "category_similarity": category_score,
            "price_similarity": price_score,
            "confidence": confidence,
        }
        calculated_weight = round((0.3 * brand_score + 0.3 * category_score + 0.2 * price_score + 0.2 * confidence), 3)

        rel = models.ProductRelationship(
            source_master_id=source_id,
            target_master_id=target_id,
            relationship_type=rel_type.value,
            confidence=confidence,
            weight=calculated_weight,
            discovery_method="auto_attribute_engine",
            creation_source="system",
            signal_breakdown=signal_breakdown,
            is_bidirectional=bidirectional,
            metadata_json=metadata,
        )
        db.add(rel)
        return {
            "source_id": source_id,
            "target_id": target_id,
            "type": rel_type.value,
            "confidence": confidence,
            "weight": calculated_weight,
            "signal_breakdown": signal_breakdown,
        }

    def get_related_masters(
        self,
        master_id: int,
        db: Session,
        relationship_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all related MasterProducts for a given master."""
        q = db.query(models.ProductRelationship).filter(
            (models.ProductRelationship.source_master_id == master_id) |
            (
                (models.ProductRelationship.target_master_id == master_id) &
                (models.ProductRelationship.is_bidirectional == True)
            )
        )

        if relationship_type:
            q = q.filter(models.ProductRelationship.relationship_type == relationship_type)

        relationships = q.order_by(models.ProductRelationship.weight.desc()).all()
        results = []
        for rel in relationships:
            other_id = rel.target_master_id if rel.source_master_id == master_id else rel.source_master_id
            other = db.query(models.MasterProduct).filter(models.MasterProduct.id == other_id).first()
            if other:
                results.append({
                    "master_id": other.id,
                    "canonical_name": other.canonical_name,
                    "brand": other.brand.name if other.brand else None,
                    "relationship_type": rel.relationship_type,
                    "confidence": rel.confidence,
                    "weight": rel.weight,
                    "signal_breakdown": rel.signal_breakdown,
                    "metadata": rel.metadata_json,
                })

        return results

    def get_weighted_graph_traversal(
        self,
        master_id: int,
        db: Session,
        depth: int = 2,
        max_nodes: int = 20,
    ) -> Dict[str, Any]:
        """
        Performs multi-hop weighted graph traversal up to max depth.
        Returns graph node network with weights and traversal paths.
        """
        visited = set()
        queue = [(master_id, 0, 1.0, [master_id])]  # (node_id, current_depth, accumulated_weight, path)
        nodes = {}
        edges = []

        start_node = db.query(models.MasterProduct).filter(models.MasterProduct.id == master_id).first()
        if not start_node:
            return {"nodes": [], "edges": [], "root_id": master_id}

        nodes[master_id] = {
            "id": start_node.id,
            "canonical_name": start_node.canonical_name,
            "brand": start_node.brand.name if start_node.brand else None,
            "depth": 0,
            "weight": 1.0,
        }

        while queue and len(nodes) < max_nodes:
            curr_id, curr_depth, curr_weight, path = queue.pop(0)
            if curr_depth >= depth:
                continue

            rels = (
                db.query(models.ProductRelationship)
                .filter(
                    (models.ProductRelationship.source_master_id == curr_id) |
                    (
                        (models.ProductRelationship.target_master_id == curr_id) &
                        (models.ProductRelationship.is_bidirectional == True)
                    )
                )
                .order_by(models.ProductRelationship.weight.desc())
                .limit(10)
                .all()
            )

            for rel in rels:
                neighbor_id = rel.target_master_id if rel.source_master_id == curr_id else rel.source_master_id
                if neighbor_id in path:
                    continue  # Avoid cycles

                neighbor = db.query(models.MasterProduct).filter(models.MasterProduct.id == neighbor_id).first()
                if not neighbor:
                    continue

                edge_weight = (rel.weight or 0.8) * curr_weight
                edges.append({
                    "source": curr_id,
                    "target": neighbor_id,
                    "type": rel.relationship_type,
                    "weight": round(edge_weight, 3),
                })

                if neighbor_id not in nodes:
                    nodes[neighbor_id] = {
                        "id": neighbor.id,
                        "canonical_name": neighbor.canonical_name,
                        "brand": neighbor.brand.name if neighbor.brand else None,
                        "depth": curr_depth + 1,
                        "weight": round(edge_weight, 3),
                    }
                    queue.append((neighbor_id, curr_depth + 1, edge_weight, path + [neighbor_id]))

        return {
            "root_id": master_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": list(nodes.values()),
            "edges": edges,
        }

