import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from sqlalchemy import DateTime, TypeDecorator, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

try:
    from pgvector.sqlalchemy import Vector as PGVector
except ImportError:
    PGVector = None


class Base(DeclarativeBase):
    """Base declarative class for all TradeTrace SQLAlchemy models."""
    pass


class UUIDMixin:
    """Provides a UUID primary key for all models."""
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """Provides UTC created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class VectorType(TypeDecorator):
    """
    Adaptive Vector column:
    Uses native pgvector Vector on PostgreSQL,
    and falls back to JSON float arrays on SQLite/other dialects.
    """
    impl = JSON
    cache_ok = True

    def __init__(self, dim: int = 1536, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and PGVector is not None:
            return dialect.type_descriptor(PGVector(self.dim))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: Optional[List[float]], dialect):
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        return value

    def process_result_value(self, value: Any, dialect) -> Optional[List[float]]:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        return value
