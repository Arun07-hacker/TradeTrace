import uuid
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, Index, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.trade import Trade


class Alert(Base, UUIDMixin, TimestampMixin):
    """User notifications and critical risk/memory alert signals."""
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    trade_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    symbol: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)  # INFO, WARNING, CRITICAL
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="alerts")
    trade: Mapped[Optional["Trade"]] = relationship("Trade")

    __table_args__ = (
        Index("ix_alerts_user_unread", "user_id", "is_read"),
        Index("ix_alerts_created_at", "created_at"),
    )
