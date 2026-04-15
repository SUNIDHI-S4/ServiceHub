"""Staff queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.staff import StaffType
from app.repositories.staff import StaffRepository


@strawberry.type
class StaffQueries:
    @strawberry.field(name="staff")
    async def staff_list(
        self, info: strawberry.Info, skip: int = 0, limit: int = 50
    ) -> list[StaffType]:
        repo = StaffRepository(info.context.db)
        rows = await repo.list_all(skip=skip, limit=limit)
        return [StaffType.from_orm(r) for r in rows]

    @strawberry.field
    async def staff_member(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> StaffType | None:
        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return StaffType.from_orm(obj) if obj else None
