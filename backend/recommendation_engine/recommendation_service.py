"""
Brand Battle — Recommendation Service Orchestrator
Central orchestrator executing multi-engine recommendation strategies, parallel scoring, personalization, caching, and audit logging.
"""

from typing import List, Dict, Any, Optional
import time
from sqlalchemy.orm import Session
from models import Product
from recommendation_engine.relationship_recommender import RelationshipRecommender
from recommendation_engine.similarity_recommender import SimilarityRecommender
from recommendation_engine.embedding_recommender import EmbeddingRecommender
from recommendation_engine.value_engine import ValueEngine
from recommendation_engine.ranking_engine import RankingEngine
from recommendation_engine.behavior_engine import BehaviorEngine
from recommendation_engine.trending_engine import TrendingEngine
from recommendation_engine.personalization_engine import PersonalizationEngine
from recommendation_engine.price_intelligence import PriceIntelligence
from recommendation_engine.recommendation_cache import RecommendationCache
from recommendation_engine.recommendation_metrics import recommendation_metrics_collector
from recommendation_engine.recommendation_history import recommendation_history_logger
from recommendation_engine.recommendation_explainer import RecommendationExplainer
from recommendation_engine.recommendation_config import recommendation_settings
from logging_config import logger


class RecommendationService:
    """Enterprise Recommendation Engine Orchestrator bringing together all engines."""

    def __init__(self):
        self.relationship_engine = RelationshipRecommender()
        self.similarity_engine = SimilarityRecommender()
        self.embedding_engine = EmbeddingRecommender()
        self.value_engine = ValueEngine()
        self.ranking_engine = RankingEngine()
        self.behavior_engine = BehaviorEngine()
        self.trending_engine = TrendingEngine()
        self.personalization_engine = PersonalizationEngine()
        self.price_engine = PriceIntelligence()
        self.cache_manager = RecommendationCache()
        self.explainer = RecommendationExplainer()

    def format_product_payload(self, item: Dict[str, Any], rec_type: str, baseline_product: Optional[Product] = None) -> Dict[str, Any]:
        """Format individual recommendation output schema."""
        p = item["product"]
        score = item.get("ranking_score", item.get("confidence", 0.85))
        explanation = self.explainer.build_explanation(
            rec_type=rec_type,
            candidate=p,
            baseline_product=baseline_product,
            score=score,
            extra_reason=item.get("reason")
        )

        return {
            "recommendation_type": rec_type,
            "confidence": round(float(score), 4),
            "ranking_score": round(float(score), 4),
            "reason": item.get("reason", explanation["primary_reason"]),
            "badge": explanation["badge"],
            "explanation": explanation,
            "product": {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "brand": p.brand.name if p.brand else None,
                "category": p.category.name if p.category else None,
                "image_url": p.image_url,
                "average_rating": p.average_rating,
                "total_reviews": p.total_reviews,
                "lowest_price": p.lowest_price,
                "current_best_price": p.current_best_price,
                "current_best_platform": p.current_best_platform,
                "deal_score": p.deal_score
            }
        }

    def get_product_recommendations(
        self, 
        db: Session, 
        product_id: int, 
        user_id: Optional[int] = None, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """Fetch comprehensive multi-category recommendations for a target product."""
        start_time = time.time()
        
        # Check Redis Cache
        cached = self.cache_manager.get_cached_recommendation("product", str(product_id))
        if cached:
            recommendation_metrics_collector.record_request(
                latency_ms=(time.time() - start_time) * 1000.0,
                cache_hit=True,
                count=len(cached.get("recommendations", []))
            )
            return cached

        product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
        if not product:
            return {"status": "error", "message": "Product not found", "recommendations": []}

        # Candidate Retrieval across engines
        rel_candidates = self.relationship_engine.get_related_products(db, product_id, limit=limit * 2)
        sim_candidates = self.similarity_engine.get_similar_spec_products(db, product, limit=limit * 2)
        emb_candidates = self.embedding_engine.get_semantic_similar_products(db, product, limit=limit * 2)
        behavior_candidates = self.behavior_engine.get_people_also_viewed(db, product_id, limit=limit * 2)

        # Merge candidates
        merged_map = {}
        for item in rel_candidates + sim_candidates + emb_candidates + behavior_candidates:
            p_id = item["product"].id
            if p_id not in merged_map:
                merged_map[p_id] = item

        raw_candidates = list(merged_map.values())
        
        # ─── MANDATORY TAXONOMY CANDIDATE FILTER ───
        from recommendation_engine.candidate_filter import candidate_filter
        from recommendation_engine.recommendation_validator import recommendation_validator

        filtered_candidates = candidate_filter.filter_candidates(product, raw_candidates)
        candidates = filtered_candidates if filtered_candidates else raw_candidates

        baseline_price = product.current_best_price or 0.0

        # Multi-factor Composite Ranking
        ranked = self.ranking_engine.rank_candidates(candidates, baseline_price=baseline_price)
        
        # Apply Personalization
        personalized = self.personalization_engine.personalize_candidates(db, user_id, ranked)

        # Formatted Payload
        formatted_list = [
            self.format_product_payload(item, rec_type="similar_specifications", baseline_product=product)
            for item in personalized
        ]

        # ─── MANDATORY AI RECOMMENDATION VALIDATION LAYER ───
        validated_list = recommendation_validator.validate_and_purge_list(product, formatted_list)[:limit]

        payload = {
            "status": "success",
            "source_product_id": product_id,
            "total": len(validated_list),
            "algorithm_version": recommendation_settings.algorithm_version,
            "recommendations": validated_list
        }

        # Cache & Audit Log
        self.cache_manager.set_cached_recommendation("product", str(product_id), payload)
        recommendation_history_logger.log_recommendation_generation(
            source_product_id=product_id,
            rec_type="multi_category",
            recommended_items=personalized[:limit],
            algorithm_version=recommendation_settings.algorithm_version,
            user_id=user_id
        )

        latency_ms = (time.time() - start_time) * 1000.0
        recommendation_metrics_collector.record_request(latency_ms=latency_ms, cache_hit=False, count=len(formatted_list))

        return payload

    def get_better_alternatives(self, db: Session, product_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """Fetch better alternatives with higher specs or ratings."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []
        sim_items = self.similarity_engine.get_similar_spec_products(db, product, limit=limit * 2)
        better = [item for item in sim_items if item["product"].average_rating and item["product"].average_rating >= (product.average_rating or 4.0)]
        return [self.format_product_payload(item, rec_type="better_alternatives", baseline_product=product) for item in better[:limit]]

    def get_budget_alternatives(self, db: Session, product_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """Fetch budget-friendly lower cost alternatives."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []
        budget_items = self.price_engine.get_budget_alternatives(db, product, limit=limit)
        return [self.format_product_payload(item, rec_type="budget_alternatives", baseline_product=product) for item in budget_items]

    def get_premium_upgrades(self, db: Session, product_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """Fetch premium hardware upgrades."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []
        upgrade_items = self.price_engine.get_premium_upgrades(db, product, limit=limit)
        return [self.format_product_payload(item, rec_type="premium_upgrades", baseline_product=product) for item in upgrade_items]

    def get_accessories(self, db: Session, product_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """Fetch accessory and complementary products."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []
        acc_items = self.relationship_engine.get_accessories(db, product_id, limit=limit)
        return [self.format_product_payload(item, rec_type="accessories", baseline_product=product) for item in acc_items]

    def get_best_value_products(self, db: Session, category_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch best value products across platform."""
        value_items = self.value_engine.get_best_value_products(db, category_id=category_id, limit=limit)
        return [self.format_product_payload(item, rec_type="best_value") for item in value_items]

    def get_trending_products(self, db: Session, category_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch high momentum trending products."""
        trending_items = self.trending_engine.get_trending_products(db, category_id=category_id, limit=limit)
        return [self.format_product_payload(item, rec_type="trending") for item in trending_items]


recommendation_orchestrator = RecommendationService()
