"""
Brand Battle — Comparison Workspace Database Models
SQLAlchemy ORM models for saved comparison sessions and decision feedback.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index
)
from database import Base


class SavedComparison(Base):
    """Saved comparison sessions with shareable link tokens."""
    __tablename__ = "workspace_saved_comparisons"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    share_token = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    product_ids_json = Column(JSON, nullable=False)
    selected_persona = Column(String(50), default="general")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DecisionFeedback(Base):
    """User decision feedback and preference tracking."""
    __tablename__ = "workspace_decision_feedback"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    chosen_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    compared_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    decision_confidence_score = Column(Float, default=95.0)
    user_persona = Column(String(50), default="general")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
