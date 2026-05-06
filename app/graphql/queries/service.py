"""Service queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.paginated import PaginatedServices
from app.graphql.types.pagination import (
    PaginationInput,
    build_page_info,
    pagination_to_offset,
)
from app.graphql.types.service import ServiceType
from app.repositories.service import ServiceRepository


@strawberry.type
class ServiceQueries:
    @strawberry.field
    async def services(
        self,
        info: strawberry.Info,
        active_only: bool = True,
        pagination: PaginationInput | None = None,
    ) -> PaginatedServices:
        pagination = pagination or PaginationInput()
        skip, limit = pagination_to_offset(pagination)
        repo = ServiceRepository(info.context.db)
        if active_only:
            rows = await repo.list_active(skip=skip, limit=limit)
            total = await repo.count_active()
        else:
            rows = await repo.list_all(skip=skip, limit=limit)
            total = await repo.count_all()
        return PaginatedServices(
            items=[ServiceType.from_orm(r) for r in rows],
            page_info=build_page_info(
                total_count=total,
                page=max(1, pagination.page),
                page_size=limit,
            ),
        )

    @strawberry.field
    async def service(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ServiceType | None:
        repo = ServiceRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return ServiceType.from_orm(obj) if obj else None
