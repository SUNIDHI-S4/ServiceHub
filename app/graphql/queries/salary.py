"""Salary queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.enums import SalaryStatusEnum
from app.graphql.types.salary import SalaryType
from app.repositories.salary import SalaryRepository


@strawberry.type
class SalaryQueries:
    @strawberry.field
    async def salaries(
        self,
        info: strawberry.Info,
        staff_id: strawberry.ID | None = None,
        status: SalaryStatusEnum | None = None,
        pay_year: int | None = None,
        pay_month: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SalaryType]:
        repo = SalaryRepository(info.context.db)
        rows = await repo.list_filtered(
            staff_id=uuid.UUID(str(staff_id)) if staff_id else None,
            status=status,
            pay_year=pay_year,
            pay_month=pay_month,
            skip=skip,
            limit=limit,
        )
        return [SalaryType.from_orm(r) for r in rows]

    @strawberry.field
    async def salary(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> SalaryType | None:
        repo = SalaryRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return SalaryType.from_orm(obj) if obj else None
