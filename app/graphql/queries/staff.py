"""Staff queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.paginated import PaginatedStaff
from app.graphql.types.pagination import (
    PaginationInput,
    build_page_info,
    pagination_to_offset,
)
from app.graphql.types.staff import StaffType
from app.repositories.staff import StaffRepository


@strawberry.type
class StaffQueries:
    @strawberry.field(name="staff")
    async def staff_list(
        self,
        info: strawberry.Info,
        pagination: PaginationInput | None = None,
    ) -> PaginatedStaff:
        pagination = pagination or PaginationInput()
        skip, limit = pagination_to_offset(pagination)
        repo = StaffRepository(info.context.db)
        rows = await repo.list_all(skip=skip, limit=limit)
        total = await repo.count_all()
        return PaginatedStaff(
            items=[StaffType.from_orm(r) for r in rows],
            page_info=build_page_info(
                total_count=total,
                page=max(1, pagination.page),
                page_size=limit,
            ),
        )

    @strawberry.field
    async def staff_member(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> StaffType | None:
        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return StaffType.from_orm(obj) if obj else None
