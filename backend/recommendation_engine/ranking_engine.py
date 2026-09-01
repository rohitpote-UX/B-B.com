"""
Brand Battle — Multi-Factor Ranking Engine
Combines multi-engine signals (relationship, similarity, value, price alignment, popularity) into composite ranking scores.
"""

from typing import List, Dict, Any
from recommendation_engine.recommendation_config import recommendation_settings
from recommendation_engine.scoring_engine import ScoringEngine
from logging_config import logger


class RankingEngine:
    """Combines individual engine scores into a final weighted recommendation ranking."""

    def __init__(self):
        self.scoring_utility = ScoringEngine()

    def rank_candidates(
        self, 
        candidates: List[Dict[str, Any]], 
        baseline_price: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Rank candidates using weighted component scoring strategy."""
        if not candidates:
            return []

        weights = recommendation_settings.weights
        ranked_results = []

        for item in candidates:
            product = item.get("product")
            if not product:
                continue

            rel_score = item.get("confidence", 0.0)
            sim_score = item.get("similarity_score", 0.0) or item.get("semantic_score", 0.0)
            val_score = (item.get("value_score", 50.0)) / 100.0
            pop_score = self.scoring_utility.evaluate_popularity(product)
            
            cand_price = getattr(product, 'current_best_price', 0.0) or 0.0
            price_score = self.scoring_utility.evaluate_price_alignment(baseline_price, cand_price) if baseline_price else 0.8

            composite_score = (
                rel_score * weights.relationship_weight +
                sim_score * weights.similarity_weight +
                val_score * weights.value_weight +
                pop_score * weights.popularity_weight +
                price_score * weights.price_alignment_weight
            )

            # Round composite score to 4 decimals
            composite_score = round(composite_score, 4)

            ranked_item = dict(item)
            ranked_item["ranking_score"] = composite_score
            ranked_item["confidence"] = max(rel_score, sim_score, val_score)
            ranked_results.append(ranked_item)

        ranked_results.sort(key=lambda x: x["ranking_score"], reverse=True)
        return ranked_results
