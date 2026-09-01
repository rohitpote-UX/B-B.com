"""
Brand Battle — Enterprise Price Intelligence Service Facade
High-level service unifying all 20 price intelligence sub-engines.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from price_intelligence.repository import price_intel_repo
from price_intelligence.price_history import price_history_engine
from price_intelligence.buy_advisor import ai_buy_advisor
from price_intelligence.fair_value_engine import fair_value_engine
from price_intelligence.fake_discount_detector import fake_discount_detector
from price_intelligence.marketplace_trust import marketplace_trust_engine
from price_intelligence.price_forecasting import price_forecasting_engine
from price_intelligence.festival_engine import festival_engine
from price_intelligence.volatility_engine import volatility_engine
from price_intelligence.value_engine import value_for_money_engine
from price_intelligence.buy_confidence import buy_confidence_engine
from price_intelligence.alert_engine import smart_alert_engine
from price_intelligence.negotiation_assistant import ai_negotiation_assistant
from price_intelligence.best_time_to_buy import best_time_to_buy_engine
from price_intelligence.hidden_cost_calculator import hidden_cost_calculator
from price_intelligence.ownership_cost import ownership_cost_engine
from price_intelligence.explanation_engine import explanation_engine
from price_intelligence.market_heat_engine import market_heat_engine
from price_intelligence.opportunity_engine import opportunity_engine
from price_intelligence.bundle_engine import smart_bundle_engine
from price_intelligence.personalization import personalized_price_engine
from price_intelligence.cache import price_intel_cache
from price_intelligence.metrics import price_intel_metrics
from price_intelligence.analytics import price_intel_analytics
from price_intelligence.config import price_intel_config

logger = logging.getLogger("brandbattle.price_intelligence.service")


class PriceIntelligenceService:
    """High-level facade orchestrating all 20 Price Intelligence modules."""

    def generate_full_report(
        self, db: Session, product_id: int, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive 20-module Price Intelligence Report targeting <50ms cached, <200ms fresh."""
        start_time = time.time()

        # 1. Check Redis Cache
        cached = price_intel_cache.get_report(product_id)
        if cached:
            latency = (time.time() - start_time) * 1000
            price_intel_metrics.record_request(latency_ms=latency, cache_hit=True)
            return cached

        # Fetch product
        product = price_intel_repo.get_product(db, product_id)
        if not product:
            return {"status": "error", "message": f"Product #{product_id} not found"}

        # 2. Execute Sub-Engines
        buy_rec = ai_buy_advisor.advise_buy(db, product)
        fair_val = fair_value_engine.calculate_fair_value(db, product)
        discount_audit = fake_discount_detector.audit_discount(db, product)
        mp_trust = marketplace_trust_engine.get_marketplace_trust(
            db, product.current_best_platform or "amazon"
        )
        forecast = price_forecasting_engine.forecast_prices(db, product)
        volatility = volatility_engine.calculate_volatility(db, product)
        hidden_costs = hidden_cost_calculator.calculate_hidden_costs(product)
        tco = ownership_cost_engine.calculate_tco(product)
        negotiation = ai_negotiation_assistant.calculate_negotiation_strategy(db, product)
        bundles = smart_bundle_engine.recommend_bundles(db, product)
        market_heat = market_heat_engine.determine_market_heat(db, product)

        # 3. Master Scores
        buy_conf = buy_confidence_engine.calculate_confidence(db, product)
        opp_score = opportunity_engine.calculate_opportunity_score(db, product)
        if user_id:
            opp_score = personalized_price_engine.personalize_opportunity(
                db, product, opp_score, user_id
            )

        # 4. Generate Narrative Explanation
        narrative = explanation_engine.generate_explanation(
            product_name=product.name,
            buy_rec=buy_rec,
            fair_value=fair_val,
            discount_audit=discount_audit,
            trust=mp_trust,
        )

        # Log Opportunity Record
        price_intel_repo.record_opportunity_score(
            db=db,
            product_id=product.id,
            score=opp_score,
            confidence=buy_conf,
            recommendation=buy_rec.decision,
            fair_value=fair_val.fair_price,
            fake_discount_detected=discount_audit.is_manipulated,
            market_heat=market_heat,
            signals=buy_rec.model_dump(),
        )

        # Build Report
        report = {
            "product_id": product.id,
            "product_name": product.name,
            "brand": product.brand.name if product.brand else None,
            "category": product.category.name if product.category else None,
            "current_best_price": product.current_best_price or 0.0,
            "original_price": getattr(product, 'highest_price', None) or getattr(product, 'current_best_price', 0.0),
            "opportunity_score": opp_score,
            "buy_confidence_score": buy_conf,
            "market_heat_status": market_heat,
            "buy_recommendation": buy_rec.model_dump(),
            "fair_market_value": fair_val.model_dump(),
            "fake_discount_audit": discount_audit.model_dump(),
            "marketplace_trust": mp_trust.model_dump(),
            "forecast": forecast.model_dump(),
            "volatility": volatility.model_dump(),
            "hidden_costs": hidden_costs.model_dump(),
            "tco": tco.model_dump(),
            "negotiation": negotiation.model_dump(),
            "bundles": [b.model_dump() for b in bundles],
            "explanation": narrative,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Cache in Redis
        price_intel_cache.set_report(product_id, report)

        latency = (time.time() - start_time) * 1000
        price_intel_metrics.record_request(latency_ms=latency, cache_hit=False)

        return report


# Singleton
price_intel_service = PriceIntelligenceService()
