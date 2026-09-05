import uuid
from datetime import datetime
from typing import Optional, Any, List, TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, Index, Text, JSON, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base, UUIDMixin, TimestampMixin, VectorType

if TYPE_CHECKING:
    from app.models.user import User


class Trade(Base, UUIDMixin, TimestampMixin):
    """Paper trade order and execution lifecycle."""
    __tablename__ = "trades"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # LONG, SHORT
    timeframe: Mapped[str] = mapped_column(String(10), default="1d", nullable=False)
    
    # Execution & Risk metrics
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    target: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    risk_amount: Mapped[float] = mapped_column(Float, nullable=False)
    risk_reward_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Thesis & AI evaluation
    thesis: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)  # STRONG_SETUP, POSSIBLE_SETUP, WAIT, HIGH_RISK, AVOID
    status: Mapped[str] = mapped_column(String(50), default="PLANNED", index=True, nullable=False)  # PLANNED, OPEN, TARGET_HIT, STOP_HIT, CLOSED_MANUALLY, CANCELLED
    
    # Outcome metrics (filled upon close)
    exit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    realized_pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    realized_pnl_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="trades")
    analysis: Mapped[Optional["TradeAnalysis"]] = relationship(
        "TradeAnalysis", back_populates="trade", uselist=False, cascade="all, delete-orphan"
    )
    events: Mapped[list["TradeEvent"]] = relationship(
        "TradeEvent", back_populates="trade", cascade="all, delete-orphan"
    )
    memory: Mapped[Optional["TradeMemory"]] = relationship(
        "TradeMemory", back_populates="trade", uselist=False, cascade="all, delete-orphan"
    )
    lessons: Mapped[list["TradeLesson"]] = relationship(
        "TradeLesson", back_populates="trade"
    )

    __table_args__ = (
        Index("ix_trades_user_status", "user_id", "status"),
        Index("ix_trades_symbol_status", "symbol", "status"),
        Index("ix_trades_created_at", "created_at"),
    )


class TradeAnalysis(Base, UUIDMixin, TimestampMixin):
    """Detailed multi-agent analytical assessment for a trade setup."""
    __tablename__ = "trade_analysis"

    trade_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    market_summary: Mapped[str] = mapped_column(Text, nullable=False)
    technical_summary: Mapped[str] = mapped_column(Text, nullable=False)
    news_summary: Mapped[str] = mapped_column(Text, nullable=False)
    
    supporting_factors: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    risk_factors: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    devils_advocate_findings: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    
    thesis_strength: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    decision_rationale: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    raw_agent_outputs: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationship
    trade: Mapped["Trade"] = relationship("Trade", back_populates="analysis")


class TradeEvent(Base, UUIDMixin, TimestampMixin):
    """Monitoring and tracking events occurring while a trade is open."""
    __tablename__ = "trade_events"

    trade_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)  # INFO, WARNING, CRITICAL
    data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationship
    trade: Mapped["Trade"] = relationship("Trade", back_populates="events")

    __table_args__ = (
        Index("ix_trade_events_trade_created", "trade_id", "created_at"),
    )


class TradeMemory(Base, UUIDMixin, TimestampMixin):
    """
    Long-term cognitive memory record of a trade:
    Contains original thesis, counter-arguments, actual outcome,
    root-cause mistake, lesson, and vector embedding for semantic search.
    """
    __tablename__ = "trade_memory"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    trade_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    setup_title: Mapped[str] = mapped_column(String(200), nullable=False)
    original_thesis: Mapped[str] = mapped_column(Text, nullable=False)
    setup_tags: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    market_context: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    devils_advocate_warnings: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    
    # Outcome & Retrospective
    outcome: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # WIN, LOSS, BREAKEVEN, PENDING
    mistake: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Vector Embedding for pgvector semantic search
    embedding: Mapped[Optional[List[float]]] = mapped_column(VectorType(dim=1536), nullable=True)

    # Relationship
    trade: Mapped["Trade"] = relationship("Trade", back_populates="memory")

    __table_args__ = (
        Index("ix_trade_memory_user_symbol", "user_id", "symbol"),
        Index("ix_trade_memory_outcome", "outcome"),
    )


class TradeLesson(Base, UUIDMixin, TimestampMixin):
    """Curated knowledge repository of trading lessons and future operating rules."""
    __tablename__ = "trade_lessons"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    setup_type: Mapped[str] = mapped_column(String(100), nullable=False)
    mistake_type: Mapped[str] = mapped_column(String(100), nullable=False)
    lesson: Mapped[str] = mapped_column(Text, nullable=False)
    future_rule: Mapped[str] = mapped_column(Text, nullable=False)
    times_applied: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Semantic embedding of lesson and future rule
    embedding: Mapped[Optional[List[float]]] = mapped_column(VectorType(dim=1536), nullable=True)

    # Relationship
    trade: Mapped[Optional["Trade"]] = relationship("Trade", back_populates="lessons")

    __table_args__ = (
        Index("ix_trade_lessons_setup_type", "setup_type"),
    )
