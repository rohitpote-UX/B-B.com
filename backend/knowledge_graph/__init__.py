"""
Brand Battle - Knowledge Graph Package
Provides the canonical Product Knowledge Graph service layer.
"""

from knowledge_graph.kg_service import KnowledgeGraphService
from knowledge_graph.normalizer_enhanced import EnhancedNormalizer
from knowledge_graph.matcher_enhanced import EnhancedMatcher
from knowledge_graph.relationship_engine import RelationshipEngine
from knowledge_graph.cache_manager import KGCacheManager
from knowledge_graph.event_bus import event_bus, DomainEvent
from knowledge_graph.completeness import completeness_calculator
from knowledge_graph.versioning import version_manager
from knowledge_graph.review_queue import review_queue_engine
from knowledge_graph.observability import log_audit_event, trace_kg_operation, get_correlation_id
