"""
Brand Battle — Price Intelligence Repository Layer
Database data access layer following the Repository Pattern for price snapshots, alert rules, and audit records.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from models import Product, MasterProduct, MarketplaceOffer
from price_intelligence.models import (
    PriceSnapshot, PriceAlertRule, MarketplaceTrustScore, OpportunityScoreRecord, DiscountAuditRecord
)


class PriceIntelligenceRepository:
    """Repository accessing database entities with clean domain isolation."""

    def get_product(self, db: Session, product_id: int) -> Optional[Product]:
        """Fetch product by ID with eager relationships."""
        return db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

    def get_price_history_snapshots(
        self, db: Session, product_id: int, days: int = 90
    ) -> List[PriceSnapshot]:
        """Fetch historical price snapshots within a time window."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            db.query(PriceSnapshot)
            .filter(
                PriceSnapshot.product_id == product_id,
                PriceSnapshot.created_at >= cutoff,
            )
            .order_by(asc(PriceSnapshot.created_at))
            .all()
        )

    def record_price_snapshot(
        self,
        db: Session,
        product_id: int,
        marketplace: str,
        price: float,
        original_price: Optional[float] = None,
        seller_name: Optional[str] = None,
        shipping_cost: float = 0.0,
        tax_amount: float = 0.0,
        coupon_discount: float = 0.0,
    ) -> PriceSnapshot:
        """Record an immutable price snapshot."""
        effective_price = price + shipping_cost + tax_amount - coupon_discount
        snapshot = PriceSnapshot(
            product_id=product_id,
            marketplace=marketplace,
            seller_name=seller_name,
            price=price,
            original_price=original_price or price,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            coupon_discount=coupon_discount,
            effective_final_price=effective_price,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    def get_marketplace_trust_score(self, db: Session, marketplace: str) -> Optional[MarketplaceTrustScore]:
        """Fetch marketplace trust score record."""
        return (
            db.query(MarketplaceTrustScore)
            .filter(func.lower(MarketplaceTrustScore.marketplace) == marketplace.lower())
            .first()
        )

    def create_price_alert(
        self,
        db: Session,
        user_id: int,
        product_id: int,
        target_price: float,
        notify_email: str,
        drop_percentage: Optional[float] = None,
        marketplace_filter: Optional[str] = None,
    ) -> PriceAlertRule:
        """Create a user price alert rule."""
        alert = PriceAlertRule(
            user_id=user_id,
            product_id=product_id,
            target_price=target_price,
            drop_percentage=drop_percentage,
            marketplace_filter=marketplace_filter,
            notify_email=notify_email,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def get_active_alerts_for_product(self, db: Session, product_id: int) -> List[PriceAlertRule]:
        """Fetch active price alerts for a product."""
        return (
            db.query(PriceAlertRule)
            .filter(
                PriceAlertRule.product_id == product_id,
                PriceAlertRule.is_active == True,
            )
            .all()
        )

    def record_opportunity_score(
        self,
        db: Session,
        product_id: int,
        score: float,
        confidence: float,
        recommendation: str,
        fair_value: float,
        fake_discount_detected: bool,
        market_heat: str,
        signals: Dict[str, Any],
    ) -> OpportunityScoreRecord:
        """Log calculated opportunity score audit record."""
        record = OpportunityScoreRecord(
            product_id=product_id,
            opportunity_score=score,
            buy_confidence_score=confidence,
            buy_recommendation=recommendation,
            fair_market_value=fair_value,
            fake_discount_detected=fake_discount_detected,
            market_heat_status=market_heat,
            signals_json=signals,
        )
        db.add(record)
        db.commit()
        return record


# Singleton
price_intel_repo = PriceIntelligenceRepository()
