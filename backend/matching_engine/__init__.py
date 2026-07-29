"""
Brand Battle - Enterprise Hybrid AI Product Matching Engine Package
Re-exports core ensemble matcher, candidate generator, feature extractor, and metrics components.
"""

from matching_engine.ensemble_matcher import hybrid_ensemble_matcher, HybridEnsembleMatcher
from matching_engine.feature_extractor import feature_extractor
from matching_engine.candidate_generator import candidate_generator
from matching_engine.confidence_engine import confidence_engine
from matching_engine.decision_engine import decision_engine, MatchingOutcome
from matching_engine.embedding_matcher import embedding_matcher
from matching_engine.matching_history import matching_history_logger
from matching_engine.training_feedback import training_feedback_repo
from matching_engine.matching_metrics import matching_metrics_collector
