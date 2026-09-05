from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Float, DateTime, Index, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin


class News(Base, UUIDMixin, TimestampMixin):
    """Normalized financial and market news items."""
    __tablename__ = "news"

    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), unique=True, index=True, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    # News analysis attributes
    sentiment: Mapped[str] = mapped_column(String(20), default="NEUTRAL", nullable=False)  # BULLISH, BEARISH, NEUTRAL
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)      # -1.0 to 1.0
    relevance: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)    # HIGH, MEDIUM, LOW
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)      # 0.0 to 1.0
    event_type: Mapped[str] = mapped_column(String(50), default="GENERAL", nullable=False)  # EARNINGS, MACRO, PRODUCT, etc.
    impact: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)        # HIGH, MEDIUM, LOW
    
    # Extra payload
    raw_payload: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_news_symbol_published", "symbol", "published_at"),
        Index("ix_news_event_type", "event_type"),
    )
