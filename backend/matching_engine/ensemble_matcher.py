"""
Brand Battle - Hybrid AI Ensemble Matcher Facade
Master orchestrator unifying candidate generation, multi-signal evaluation,
semantic vector similarity, ensemble confidence calculation, decision outcome,
review queue triggering, audit logging, and deterministic fallback.
"""

import time
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
import logging

from matching_engine.feature_extractor import feature_extractor
from matching_engine.candidate_generator import candidate_generator
from matching_engine.title_matcher import title_matcher
from matching_engine.brand_matcher import brand_matcher
from matching_engine.category_matcher import category_matcher
from matching_engine.attribute_matcher import attribute_matcher
from matching_engine.specification_matcher import specification_matcher
from matching_engine.embedding_matcher import embedding_matcher
from matching_engine.price_matcher import price_matcher
from matching_engine.confidence_engine import confidence_engine
from matching_engine.decision_engine import decision_engine, MatchingOutcome
from matching_engine.review_trigger import review_trigger
from matching_engine.matching_history import matching_history_logger
from matching_engine.matching_metrics import matching_metrics_collector

logger = logging.getLogger("brandbattle.matching.ensemble")


class HybridEnsembleMatcher:
    """
    Central hybrid matching platform.
    Evaluates incoming marketplace listings against candidate MasterProducts.
    Includes deterministic fallback if any AI component encounters an exception.
    """

    def match_listing(
        self,
        item: Dict[str, Any],
        candidates: Optional[List[Dict[str, Any]]] = None,
        db: Session = None,
    ) -> Tuple[Optional[Dict[str, Any]], float, Dict[str, Any]]:
        """
        Orchestrates full hybrid AI matching workflow for a single listing item.

        Returns: (best_candidate_dict or None, confidence_score, explainability_dict)
        """
        start_time = time.time()
        fallback_used = False

        # 1. Feature Extraction
        features = feature_extractor.extract_features(item)
        title = features["clean_title"]
        brand = features["brand"]
        category = features["category"]

        # 2. Candidate Generation (if not explicitly provided)
        if candidates is None and db is not None:
            candidates = candidate_generator.retrieve_candidates(features, db)
        elif candidates is None:
            candidates = []

        if not candidates:
            # No candidates exist -> Decision: Create New Master
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            explainability = {
                "decision": MatchingOutcome.CREATE_NEW_MASTER,
                "confidence": 0.0,
                "reason": "No candidate MasterProducts found in database",
                "explainability": {}
            }
            if db:
                matching_history_logger.log_decision(
                    listing_title=title,
                    marketplace=features.get("marketplace", "unknown"),
                    candidates_count=0,
                    winning_candidate_id=None,
                    decision=MatchingOutcome.CREATE_NEW_MASTER,
                    confidence_score=0.0,
                    signal_breakdown={},
                    explainability=explainability,
                    execution_time_ms=elapsed_ms,
                    db=db
                )
            matching_metrics_collector.record_match_attempt(MatchingOutcome.CREATE_NEW_MASTER)
            return None, 0.0, explainability

        best_candidate = None
        highest_confidence = 0.0
        best_signals = {}
        best_decision_info = {}

        # 3. Evaluate each candidate across all 8+ matching signals
        for candidate in candidates:
            try:
                # 3a. Deterministic & Fuzzy Matchers
                title_sig = title_matcher.evaluate(title, candidate["canonical_name"])
                brand_sig = brand_matcher.evaluate(brand, candidate.get("brand_name", ""))
                cat_sig = category_matcher.evaluate(category, candidate.get("category_name", ""), features.get("subcategory"), candidate.get("subcategory_name"))
                attr_sig = attribute_matcher.evaluate(features, candidate)
                spec_sig = specification_matcher.evaluate(features.get("specs", {}), candidate.get("specifications", {}))
                price_sig = price_matcher.evaluate(features.get("price", 0.0), candidate.get("lowest_price"))

                # 3b. Semantic Vector Embedding Matcher
                # Combine title + specs for semantic string representation
                cand_specs_text = " ".join(f"{k}:{v}" for k, v in candidate.get("specifications", {}).items())
                item_specs_text = " ".join(f"{k}:{v}" for k, v in features.get("specs", {}).items())

                repr1 = f"{title} {item_specs_text}".strip()
                repr2 = f"{candidate['canonical_name']} {cand_specs_text}".strip()

                embed_sig = embedding_matcher.evaluate(repr1, repr2)

                # Model token overlap signal
                tokens1 = set(features.get("normalized_tokens", []))
                tokens2 = set(feature_extractor.extract_normalized_tokens(candidate["canonical_name"]))
                overlap = len(tokens1.intersection(tokens2)) / max(1, max(len(tokens1), len(tokens2)))
                token_sig = {"score": round(overlap, 3), "explanation": f"Token overlap: {len(tokens1.intersection(tokens2))} tokens"}

                signals = {
                    "title_similarity": title_sig,
                    "brand_match": brand_sig,
                    "model_token_overlap": token_sig,
                    "semantic_embedding": embed_sig,
                    "attribute_match": attr_sig,
                    "spec_similarity": spec_sig,
                    "category_match": cat_sig,
                    "price_similarity": price_sig,
                }

                # 4. Ensemble Confidence Engine
                ensemble = confidence_engine.compute_ensemble_confidence(signals)
                conf = ensemble["ensemble_confidence"]

                if conf > highest_confidence:
                    highest_confidence = conf
                    best_candidate = candidate
                    best_signals = signals
                    best_decision_info = ensemble

            except Exception as e:
                logger.error(f"Error evaluating candidate {candidate.get('id')}: {e}. Falling back to rule matcher.")
                fallback_used = True
                # Rule-based fallback
                b_score = brand_matcher.evaluate(brand, candidate.get("brand_name", ""))["score"]
                t_score = title_matcher.evaluate(title, candidate["canonical_name"])["score"]
                conf = (b_score * 0.5) + (t_score * 0.5)
                if conf > highest_confidence:
                    highest_confidence = conf
                    best_candidate = candidate
                    best_signals = {"brand_match": {"score": b_score}, "title_similarity": {"score": t_score}}
                    best_decision_info = {"ensemble_confidence": conf, "gated_by": None, "explainability": {}}

        # 5. Decision Engine
        decision_result = decision_engine.determine_decision(best_decision_info, category=category)
        decision = decision_result["decision"]
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        explainability_payload = {
            "decision": decision,
            "confidence": highest_confidence,
            "threshold_used": decision_result.get("threshold_used"),
            "reason": decision_result.get("reason"),
            "winning_candidate": {
                "id": best_candidate["id"] if best_candidate else None,
                "canonical_name": best_candidate["canonical_name"] if best_candidate else None,
                "public_id": best_candidate.get("public_id") if best_candidate else None,
            } if best_candidate else None,
            "signal_breakdown": best_decision_info.get("explainability", {}),
            "fallback_used": fallback_used,
            "execution_time_ms": elapsed_ms,
        }

        # 6. Human Review Queue Placement if uncertain
        if db:
            review_trigger.trigger_review_if_needed(
                item_features=features,
                best_candidate=best_candidate,
                decision_info=decision_result,
                explainability=explainability_payload,
                db=db
            )

        # 7. Audit Logging to MatchingHistoryLog
        if db:
            matching_history_logger.log_decision(
                listing_title=title,
                marketplace=features.get("marketplace", "unknown"),
                candidates_count=len(candidates),
                winning_candidate_id=best_candidate["id"] if best_candidate and decision == MatchingOutcome.AUTO_MATCH else None,
                decision=decision,
                confidence_score=highest_confidence,
                signal_breakdown=best_decision_info.get("explainability", {}),
                explainability=explainability_payload,
                execution_time_ms=elapsed_ms,
                fallback_used=fallback_used,
                db=db
            )

        matching_metrics_collector.record_match_attempt(decision, fallback_used=fallback_used)

        if decision == MatchingOutcome.AUTO_MATCH and best_candidate:
            logger.info(
                f"🎯 Ensemble Match: '{title[:30]}' -> Master #{best_candidate['id']} "
                f"'{best_candidate['canonical_name'][:30]}' [Conf: {highest_confidence:.3f}, {elapsed_ms}ms]"
            )
            return best_candidate, highest_confidence, explainability_payload

        logger.info(
            f"ℹ️ Ensemble Outcome '{decision}': '{title[:30]}' "
            f"[Best conf: {highest_confidence:.3f}, {elapsed_ms}ms]"
        )
        return None, highest_confidence, explainability_payload


# Global singleton instance
hybrid_ensemble_matcher = HybridEnsembleMatcher()
