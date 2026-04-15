"""Strawberry context wiring — bridges FastAPI DI to GraphQL resolvers."""
from __future__ import annotations

import asyncio

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.database import get_db


class Context(BaseContext):
    """Request-scoped context passed to every resolver as `info.context`.

    `db_lock` serializes DB operations across sibling resolvers. Strawberry
    runs sibling fields with `asyncio.gather`, but an `AsyncSession` cannot
    be used concurrently — see SQLAlchemy error code `isce`. The lock keeps
    the single-transaction-per-request model while preventing overlap.
    """

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db
        self.db_lock = asyncio.Lock()


async def get_context(db: AsyncSession = Depends(get_db)) -> Context:
    """FastAPI-managed context factory passed to the Strawberry router."""
    return Context(db=db)
