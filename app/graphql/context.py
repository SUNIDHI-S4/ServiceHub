"""Strawberry context wiring — bridges FastAPI DI to GraphQL resolvers."""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.database import get_db


class Context(BaseContext):
    """Request-scoped context passed to every resolver as `info.context`.

    Must subclass `strawberry.fastapi.BaseContext` — Strawberry's FastAPI
    integration rejects any other class (it only accepts `BaseContext`
    subclasses or plain dicts).
    """

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db


async def get_context(db: AsyncSession = Depends(get_db)) -> Context:
    """FastAPI-managed context factory passed to the Strawberry router.

    The DB session is request-scoped and auto-committed/rolled-back by
    the `get_db` dependency. Resolvers access it via `info.context.db`.
    """
    return Context(db=db)
