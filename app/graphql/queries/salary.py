"""Salary queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.enums import SalaryStatusEnum
from app.graphql.types.paginated import PaginatedSalaries
from app.graphql.types.pagination import (
    PaginationInput,
    build_page_info,
    pagination_to_offset,
)
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
        pagination: PaginationInput | None = None,
    ) -> PaginatedSalaries:
        pagination = pagination or PaginationInput()
        skip, limit = pagination_to_offset(pagination)
        filter_kwargs = dict(
            staff_id=uuid.UUID(str(staff_id)) if staff_id else None,
            status=status,
            pay_year=pay_year,
            pay_month=pay_month,
        )
        repo = SalaryRepository(info.context.db)
        rows = await repo.list_filtered(**filter_kwargs, skip=skip, limit=limit)
        total = await repo.count_filtered(**filter_kwargs)
        return PaginatedSalaries(
            items=[SalaryType.from_orm(r) for r in rows],
            page_info=build_page_info(
                total_count=total,
                page=max(1, pagination.page),
                page_size=limit,
            ),
        )

    @strawberry.field
    async def salary(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> SalaryType | None:
        repo = SalaryRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return SalaryType.from_orm(obj) if obj else None
