"""
Brand Battle — Affiliate Platform Repository Layer
Database data access layer following the Repository Pattern for links, clicks, and conversions.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from affiliate_platform.models import (
    EnterpriseAffiliateProvider,
    EnterpriseAffiliateLink,
    EnterpriseAffiliateClick,
    EnterpriseAffiliateConversion,
    EnterpriseAffiliateDisclosure,
)


class AffiliateRepository:
    """Repository managing database access for the Affiliate Commerce Platform."""

    def record_link(
        self,
        db: Session,
        link_token: str,
        product_id: int,
        provider_key: str,
        destination_url: str,
        affiliate_url: str,
    ) -> EnterpriseAffiliateLink:
        """Record generated affiliate link."""
        link = EnterpriseAffiliateLink(
            link_token=link_token,
            product_id=product_id,
            provider_key=provider_key,
            destination_url=destination_url,
            affiliate_url=affiliate_url,
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    def get_link_by_token(self, db: Session, link_token: str) -> Optional[EnterpriseAffiliateLink]:
        """Fetch link by token."""
        return db.query(EnterpriseAffiliateLink).filter(EnterpriseAffiliateLink.link_token == link_token).first()

    def record_click(
        self,
        db: Session,
        click_id: str,
        link_token: str,
        product_id: int,
        provider_key: str,
        session_id: str,
        touchpoint: str,
        is_fraud: bool = False,
    ) -> EnterpriseAffiliateClick:
        """Record outbound click log."""
        link = self.get_link_by_token(db, link_token)
        link_id = link.id if link else 1

        click = EnterpriseAffiliateClick(
            click_id=click_id,
            link_id=link_id,
            product_id=product_id,
            provider_key=provider_key,
            session_id=session_id,
            touchpoint=touchpoint,
            is_suspicious_fraud=is_fraud,
        )
        db.add(click)
        db.commit()
        db.refresh(click)
        return click

    def record_conversion(
        self,
        db: Session,
        conversion_id: str,
        provider_key: str,
        sale_amount: float,
        commission_amount: float,
        order_id: Optional[str] = None,
        click_id: Optional[str] = None,
    ) -> EnterpriseAffiliateConversion:
        """Record conversion transaction."""
        conv = EnterpriseAffiliateConversion(
            conversion_id=conversion_id,
            provider_key=provider_key,
            order_id=order_id,
            click_id=click_id,
            sale_amount_inr=sale_amount,
            commission_amount_inr=commission_amount,
            status="approved",
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv


# Singleton
affiliate_repo = AffiliateRepository()
