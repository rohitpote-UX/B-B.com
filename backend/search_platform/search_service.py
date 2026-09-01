"""
Brand Battle — Search Service Facade
High-level service wrapping the SearchOrchestrator for API consumption.
"""

import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from search_platform.search_orchestrator import search_orchestrator
from search_platform.autocomplete_engine import autocomplete_engine
from search_platform.facet_engine import facet_engine
from search_platform.search_cache import search_cache
from search_platform.analytics import search_analytics
from search_platform.metrics import search_metrics
from search_platform.history import search_history_logger
from search_platform.feedback import search_feedback
from search_platform.config import search_config

logger = logging.getLogger("brandbattle.search.service")


class SearchService:
    """High-level search service facade for API endpoint consumption."""

    def search(
        self,
        query: str,
        db: Session,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a full AI-powered search."""
        try:
            return search_orchestrator.execute_search(
                raw_query=query,
                db=db,
                user_id=user_id,
                page=page,
                page_size=page_size,
                filters=filters,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Search execution error: {e}")
            search_metrics.record_error()
            return {
                "query": {"raw": query},
                "results": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "error": str(e),
            }

    def autocomplete(
        self,
        prefix: str,
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get autocomplete suggestions."""
        start = time.time()
        try:
            result = autocomplete_engine.suggest(prefix, db, user_id=user_id, limit=limit)
            latency = (time.time() - start) * 1000
            search_metrics.record_autocomplete_request(latency)
            return result
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return {"suggestions": [], "prefix": prefix}

    def get_facets(
        self,
        query: str,
        db: Session,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get dynamic faceted filters for a query."""
        try:
            # Check cache first
            cached = search_cache.get_facet_cache(query)
            if cached:
                return cached

            # Run a quick search to get result set, then generate facets
            results = search_orchestrator.execute_search(
                raw_query=query, db=db, page=1, page_size=100
            )

            product_ids = [
                r["product"]["id"] for r in results.get("results", [])
            ]

            facets = facet_engine.generate_facets(product_ids, db)

            # Cache facets
            search_cache.set_facet_cache(query, facets)

            return facets

        except Exception as e:
            logger.error(f"Facet generation error: {e}")
            return {"facets": []}

    def get_suggestions(self, db: Session) -> Dict[str, Any]:
        """Get popular and trending search suggestions."""
        try:
            # Check cache
            cached = search_cache.get_popular_queries()
            if cached:
                return cached

            analytics = search_analytics.get_analytics_summary()
            suggestions = {
                "popular_searches": analytics.get("top_searches", [])[:10],
                "trending_searches": analytics.get("top_searches", [])[:5],
            }

            search_cache.set_popular_queries(suggestions)
            return suggestions

        except Exception as e:
            logger.error(f"Suggestion retrieval error: {e}")
            return {"popular_searches": [], "trending_searches": []}

    def record_feedback(
        self,
        query: str,
        product_id: int,
        position: int,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record search result click feedback."""
        try:
            search_feedback.record_click(
                query=query,
                product_id=product_id,
                position=position,
                user_id=user_id,
                session_id=session_id,
            )
            search_analytics.record_click(query, product_id, position)
            return {"success": True, "message": "Feedback recorded"}
        except Exception as e:
            logger.error(f"Feedback recording error: {e}")
            return {"success": False, "message": str(e)}

    def get_user_history(
        self, user_id: int, db: Session, limit: int = 20
    ) -> Dict[str, Any]:
        """Get user's search history."""
        try:
            entries = search_history_logger.get_user_history(user_id, db, limit)
            return {"history": entries, "total": len(entries)}
        except Exception as e:
            logger.error(f"History retrieval error: {e}")
            return {"history": [], "total": 0}

    def get_metrics(self) -> Dict[str, Any]:
        """Get search platform observability metrics."""
        return search_metrics.get_metrics()

    def get_analytics(self) -> Dict[str, Any]:
        """Get search analytics summary."""
        return search_analytics.get_analytics_summary()

    def health_check(self) -> Dict[str, Any]:
        """Search platform health check."""
        from redis_client import is_redis_healthy
        return {
            "status": "healthy" if search_config.enabled else "disabled",
            "algorithm_version": search_config.algorithm_version,
            "redis_cache": "connected" if is_redis_healthy() else "disconnected",
            "features": {
                "semantic_search": search_config.enable_semantic_search,
                "kg_search": search_config.enable_kg_search,
                "spell_correction": search_config.enable_spell_correction,
                "synonyms": search_config.enable_synonyms,
                "personalization": search_config.enable_personalization,
                "reranking": search_config.enable_reranking,
                "analytics": search_config.enable_analytics,
            },
        }


# Singleton
search_service = SearchService()
