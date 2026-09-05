import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.trade import Trade


class Portfolio(Base, UUIDMixin, TimestampMixin):
    """Paper trading portfolio balance and summary metrics."""
    __tablename__ = "portfolio"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    initial_balance: Mapped[float] = mapped_column(Float, default=100000.0, nullable=False)
    cash_balance: Mapped[float] = mapped_column(Float, default=100000.0, nullable=False)
    total_equity: Mapped[float] = mapped_column(Float, default=100000.0, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    win_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    loss_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_drawdown_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_exposure_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="portfolio")
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="portfolio", cascade="all, delete-orphan"
    )


class Position(Base, UUIDMixin, TimestampMixin):
    """Active open market positions in paper trading portfolio."""
    __tablename__ = "positions"

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("portfolio.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    trade_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # LONG, SHORT
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    target: Mapped[float] = mapped_column(Float, nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unrealized_pnl_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationship
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="positions")
    trade: Mapped["Trade"] = relationship("Trade")

    __table_args__ = (
        Index("ix_positions_portfolio_symbol", "portfolio_id", "symbol"),
    )
