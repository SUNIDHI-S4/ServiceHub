"""Async SQLAlchemy engine, session factory, and FastAPI dependency."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# `pool_pre_ping=True` issues a lightweight SELECT 1 before handing out a
# pooled connection. Required for Supabase, which aggressively drops idle
# connections and would otherwise return stale sockets to the caller.
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_pre_ping=True,
    echo=settings.debug,
)

# `expire_on_commit=False` is mandatory for async SQLAlchemy. Without it,
# attribute access after commit triggers an implicit lazy load, which is
# synchronous and raises MissingGreenlet inside an async context.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a transactional AsyncSession.

    Commits on successful request completion, rolls back on any exception.
    Repositories should call `session.flush()` rather than `commit()` so
    that multi-step mutations stay atomic within a single request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
