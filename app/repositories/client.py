"""Client repository."""
from __future__ import annotations

from sqlalchemy import select

from app.models.client import Client
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    model = Client

    async def get_by_email(self, email: str) -> Client | None:
        result = await self.db.execute(select(Client).where(Client.email == email))
        return result.scalar_one_or_none()
