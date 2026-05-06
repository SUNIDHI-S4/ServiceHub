"""Client queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.client import ClientType
from app.graphql.types.paginated import PaginatedClients
from app.graphql.types.pagination import (
    PaginationInput,
    build_page_info,
    pagination_to_offset,
)
from app.repositories.client import ClientRepository


@strawberry.type
class ClientQueries:
    @strawberry.field
    async def clients(
        self,
        info: strawberry.Info,
        pagination: PaginationInput | None = None,
    ) -> PaginatedClients:
        pagination = pagination or PaginationInput()
        skip, limit = pagination_to_offset(pagination)
        repo = ClientRepository(info.context.db)
        rows = await repo.list_all(skip=skip, limit=limit)
        total = await repo.count_all()
        return PaginatedClients(
            items=[ClientType.from_orm(r) for r in rows],
            page_info=build_page_info(
                total_count=total,
                page=max(1, pagination.page),
                page_size=limit,
            ),
        )

    @strawberry.field
    async def client(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ClientType | None:
        repo = ClientRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return ClientType.from_orm(obj) if obj else None
