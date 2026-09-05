import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio
    from app.models.trade import Trade
    from app.models.alert import Alert


class User(Base, UUIDMixin, TimestampMixin):
    """User account model."""
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    preference: Mapped[Optional["UserPreference"]] = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    portfolio: Mapped[Optional["Portfolio"]] = relationship(
        "Portfolio", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="user", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="user", cascade="all, delete-orphan"
    )


class UserPreference(Base, UUIDMixin, TimestampMixin):
    """User trading preferences and risk tolerance."""
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    preferred_market: Mapped[str] = mapped_column(String(50), default="US_EQUITIES", nullable=False)
    risk_preference: Mapped[str] = mapped_column(String(50), default="MODERATE", nullable=False)
    default_risk_pct: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_portfolio_exposure_pct: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    enable_memory_warnings: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_monitoring_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="preference")
