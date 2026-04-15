"""Service queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.service import ServiceType
from app.repositories.service import ServiceRepository


@strawberry.type
class ServiceQueries:
    @strawberry.field
    async def services(
        self,
        info: strawberry.Info,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ServiceType]:
        repo = ServiceRepository(info.context.db)
        if active_only:
            rows = await repo.list_active(skip=skip, limit=limit)
        else:
            rows = await repo.list_all(skip=skip, limit=limit)
        return [ServiceType.from_orm(r) for r in rows]

    @strawberry.field
    async def service(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ServiceType | None:
        repo = ServiceRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return ServiceType.from_orm(obj) if obj else None
