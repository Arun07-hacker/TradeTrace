from datetime import datetime
from sqlalchemy import String, Float, DateTime, Index, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin


class Symbol(Base, UUIDMixin, TimestampMixin):
    """Tradable asset symbol metadata."""
    __tablename__ = "symbols"

    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(50), default="EQUITY", nullable=False)
    exchange: Mapped[str] = mapped_column(String(50), default="NASDAQ", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_symbols_symbol_active", "symbol", "is_active"),
    )


class MarketData(Base, UUIDMixin, TimestampMixin):
    """Historical and real-time OHLCV market data."""
    __tablename__ = "market_data"

    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), default="1d", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    vwap: Mapped[float] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_market_data_symbol_timestamp", "symbol", "timestamp"),
        Index("ix_market_data_symbol_tf_ts", "symbol", "timeframe", "timestamp"),
    )
