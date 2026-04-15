"""Client queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.client import ClientType
from app.repositories.client import ClientRepository


@strawberry.type
class ClientQueries:
    @strawberry.field
    async def clients(
        self, info: strawberry.Info, skip: int = 0, limit: int = 50
    ) -> list[ClientType]:
        repo = ClientRepository(info.context.db)
        rows = await repo.list_all(skip=skip, limit=limit)
        return [ClientType.from_orm(r) for r in rows]

    @strawberry.field
    async def client(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ClientType | None:
        repo = ClientRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return ClientType.from_orm(obj) if obj else None
