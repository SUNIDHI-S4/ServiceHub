"""Service repository."""
from __future__ import annotations

from sqlalchemy import select

from app.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    model = Service

    async def list_active(self, skip: int = 0, limit: int = 50) -> list[Service]:
        result = await self.db.execute(
            select(Service)
            .where(Service.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
