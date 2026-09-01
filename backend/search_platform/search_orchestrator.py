"""
Brand Battle — Search Orchestrator
Central coordinator executing the full search pipeline:
Parse -> Classify -> Normalize -> Spell Correct -> Synonym Expand
-> Candidate Generation -> Parallel Retrieval -> Merge -> Rank -> Re-Rank
-> Personalize -> Explain -> Cache -> Response

No module calls another directly — all coordination flows through this orchestrator.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from search_platform.config import search_config
from search_platform.query_parser import query_parser, ParsedQuery
from search_platform.query_classifier import query_classifier, QueryClassification
from search_platform.query_normalizer import query_normalizer
from search_platform.spell_corrector import spell_corrector
from search_platform.synonym_engine import synonym_engine
from search_platform.intent_detector import intent_detector, ShoppingIntent
from search_platform.candidate_generator import candidate_generator
from search_platform.keyword_search import keyword_search
from search_platform.semantic_search import semantic_search
from search_platform.knowledge_graph_search import knowledge_graph_search
from search_platform.attribute_search import attribute_search
from search_platform.marketplace_search import marketplace_search
from search_platform.ranking_engine import ranking_engine
from search_platform.reranking_engine import reranking_engine
from search_platform.personalization_engine import search_personalization
from search_platform.search_explainer import search_explainer
from search_platform.search_cache import search_cache
from search_platform.analytics import search_analytics
from search_platform.metrics import search_metrics
from search_platform.history import search_history_logger
from search_platform.feedback import search_feedback

logger = logging.getLogger("brandbattle.search.orchestrator")


class SearchOrchestrator:
    """Central search pipeline orchestrator coordinating all search modules."""

    def execute_search(
        self,
        raw_query: str,
        db: Session,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full search pipeline from raw query to ranked, explained results.
        """
        total_start = time.time()
        filters = filters or {}

        # ─── Stage 0: Cache Check ────────────────────────────────────
        cache_key_query = f"{raw_query}|p{page}|ps{page_size}"
        cached = search_cache.get_query_result(cache_key_query, filters)
        if cached:
            latency = (time.time() - total_start) * 1000
            search_metrics.record_search_request(total_ms=latency, cache_hit=True)
            search_analytics.record_search(
                raw_query, cached.get("total", 0), latency, filters, cache_hit=True
            )
            return cached

        # ─── Stage 1: Query Parsing ──────────────────────────────────
        parse_start = time.time()
        parsed = query_parser.parse(raw_query, db)
        parse_ms = (time.time() - parse_start) * 1000

        # ─── Stage 2: Query Classification ───────────────────────────
        classification = query_classifier.classify(parsed)

        # ─── Stage 3: Query Normalization ────────────────────────────
        normalized_tokens = query_normalizer.normalize(parsed.remaining_keywords)

        # ─── Stage 4: Spell Correction ───────────────────────────────
        spell_result = {"was_corrected": False, "corrected_tokens": normalized_tokens}
        if search_config.enable_spell_correction:
            spell_result = spell_corrector.correct_query(normalized_tokens, db)

        corrected_tokens = spell_result["corrected_tokens"]

        # ─── Stage 5: Synonym Expansion ──────────────────────────────
        expanded_tokens = corrected_tokens
        if search_config.enable_synonyms:
            expanded_tokens = synonym_engine.expand_tokens(corrected_tokens)

        # ─── Intent Detection ────────────────────────────────────────
        intent = intent_detector.detect(parsed, classification)

        # ─── Stage 6: Candidate Generation ───────────────────────────
        retrieval_start = time.time()
        candidate_ids = candidate_generator.generate(parsed, db)

        # ─── Stage 7: Hybrid Retrieval (parallel engines) ────────────
        # Build the search text from expanded tokens + brand + category
        search_text_parts = list(expanded_tokens)
        if parsed.brand:
            search_text_parts.append(parsed.brand)
        if parsed.product_type:
            search_text_parts.append(parsed.product_type)
        search_text = " ".join(search_text_parts)

        # 7a. Keyword Search
        kw_results = keyword_search.search(expanded_tokens, candidate_ids, db)

        # 7b. Semantic Search
        sem_results = semantic_search.search(search_text, candidate_ids, db)

        # 7c. Knowledge Graph Search
        kg_results = knowledge_graph_search.search(parsed, candidate_ids, db)

        # 7d. Attribute Search
        attr_results = attribute_search.search(parsed, candidate_ids, db)

        # 7e. Marketplace Search
        mp_results = marketplace_search.search(parsed, candidate_ids, db)

        retrieval_ms = (time.time() - retrieval_start) * 1000

        # ─── Merge Candidates ────────────────────────────────────────
        merged = self._merge_candidates(kw_results, sem_results, kg_results, attr_results, mp_results)

        # ─── Stage 8: Ranking ────────────────────────────────────────
        ranking_start = time.time()
        ranked = ranking_engine.rank(merged, parsed_query=parsed, user_id=user_id)
        ranking_ms = (time.time() - ranking_start) * 1000

        # ─── Stage 9: Re-Ranking ─────────────────────────────────────
        rerank_start = time.time()
        reranked = reranking_engine.rerank(ranked, intent=intent)
        rerank_ms = (time.time() - rerank_start) * 1000

        # ─── Stage 13: Personalization ───────────────────────────────
        if search_config.enable_personalization and user_id:
            p_signals = search_personalization.get_personalization_signals(user_id, db)
            reranked = search_personalization.apply_personalization(reranked, p_signals)
            # Re-sort after personalization
            reranked.sort(
                key=lambda x: x.get("reranked_score", x.get("composite_score", 0))
                + x.get("personalization_score", 0) * 0.1,
                reverse=True,
            )

        # ─── Pagination ──────────────────────────────────────────────
        total_results = len(reranked)
        page_size = min(page_size, search_config.max_page_size)
        offset = (page - 1) * page_size
        page_results = reranked[offset:offset + page_size]
        total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 0

        # ─── Stage 10: Explainability ────────────────────────────────
        formatted_results = []
        for item in page_results:
            product = item.get("product")
            if not product:
                continue

            explanation = search_explainer.explain_result(
                product=product,
                signal_breakdown=item.get("signal_breakdown", {}),
                composite_score=item.get("reranked_score", item.get("composite_score", 0.0)),
                query_brand=parsed.brand,
            )

            formatted_results.append({
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "slug": product.slug,
                    "brand": product.brand.name if product.brand else None,
                    "category": product.category.name if product.category else None,
                    "image_url": product.image_url,
                    "average_rating": product.average_rating,
                    "total_reviews": product.total_reviews,
                    "lowest_price": product.lowest_price,
                    "current_best_price": product.current_best_price,
                    "current_best_platform": product.current_best_platform,
                    "deal_score": product.deal_score,
                },
                "relevance": explanation,
            })

        total_ms = (time.time() - total_start) * 1000

        # ─── Build Response ──────────────────────────────────────────
        response = {
            "query": {
                "raw": raw_query,
                "parsed": parsed.to_dict(),
                "classification": classification.to_dict(),
                "intent": intent.to_dict(),
                "spell_correction": {
                    "was_corrected": spell_result["was_corrected"],
                    "did_you_mean": spell_result.get("did_you_mean"),
                    "corrections": spell_result.get("corrections", []),
                },
            },
            "results": formatted_results,
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "performance": {
                "total_ms": round(total_ms, 2),
                "parse_ms": round(parse_ms, 2),
                "retrieval_ms": round(retrieval_ms, 2),
                "ranking_ms": round(ranking_ms, 2),
                "reranking_ms": round(rerank_ms, 2),
            },
            "algorithm_version": search_config.algorithm_version,
        }

        # ─── Cache Result ────────────────────────────────────────────
        search_cache.set_query_result(cache_key_query, filters, response)

        # ─── Record Metrics & Analytics ──────────────────────────────
        search_metrics.record_search_request(
            total_ms=total_ms,
            parse_ms=parse_ms,
            retrieval_ms=retrieval_ms,
            ranking_ms=ranking_ms,
            reranking_ms=rerank_ms,
            cache_hit=False,
        )

        search_analytics.record_search(
            query=raw_query,
            results_count=total_results,
            latency_ms=total_ms,
            filters=filters,
            was_corrected=spell_result["was_corrected"],
            cache_hit=False,
        )

        # ─── Log Search History ──────────────────────────────────────
        search_history_logger.log_search(
            db=db,
            raw_query=raw_query,
            parsed_query=parsed.to_dict(),
            intent=intent.intent_type,
            classification=classification.primary,
            filters=filters,
            results_count=total_results,
            latency_ms=total_ms,
            user_id=user_id,
            session_id=session_id,
            was_corrected=spell_result["was_corrected"],
            corrected_query=spell_result.get("did_you_mean"),
            algorithm_version=search_config.algorithm_version,
        )

        return response

    def _merge_candidates(self, *result_lists) -> List[Dict[str, Any]]:
        """Merge candidate lists from multiple retrieval engines, deduplicating by product ID."""
        seen_ids = set()
        merged = []

        for results in result_lists:
            for item in results:
                product = item.get("product")
                if product and product.id not in seen_ids:
                    seen_ids.add(product.id)
                    merged.append(item)
                elif product and product.id in seen_ids:
                    # Merge scores into existing candidate
                    for existing in merged:
                        if existing.get("product") and existing["product"].id == product.id:
                            for key in ["keyword_score", "semantic_score", "kg_score",
                                        "attribute_score", "marketplace_score"]:
                                if key in item and item[key] > existing.get(key, 0.0):
                                    existing[key] = item[key]
                            break

        return merged


# Singleton
search_orchestrator = SearchOrchestrator()
