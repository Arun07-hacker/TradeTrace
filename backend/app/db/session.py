from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.db.base import Base

# Determine engine URL
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite fallback parameters
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for yielding async database sessions."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db(custom_engine=None) -> None:
    """Initialize database tables and enable pgvector extension if PostgreSQL."""
    target_engine = custom_engine or engine
    async with target_engine.begin() as conn:
        # If dialect is postgresql, enable vector extension
        if target_engine.dialect.name == "postgresql":
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            except Exception as e:
                print(f"[DB Warning] Could not create pgvector extension: {e}")
        
        await conn.run_sync(Base.metadata.create_all)
