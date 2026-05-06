"""Expense queries."""
from __future__ import annotations

import uuid
from datetime import date

import strawberry

from app.graphql.types.enums import ExpenseCategoryEnum, ExpenseStatusEnum
from app.graphql.types.expense import ExpenseType
from app.graphql.types.paginated import PaginatedExpenses
from app.graphql.types.pagination import (
    PaginationInput,
    build_page_info,
    pagination_to_offset,
)
from app.repositories.expense import ExpenseRepository


@strawberry.type
class ExpenseQueries:
    @strawberry.field
    async def expenses(
        self,
        info: strawberry.Info,
        status: ExpenseStatusEnum | None = None,
        category: ExpenseCategoryEnum | None = None,
        staff_id: strawberry.ID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        pagination: PaginationInput | None = None,
    ) -> PaginatedExpenses:
        pagination = pagination or PaginationInput()
        skip, limit = pagination_to_offset(pagination)
        filter_kwargs = dict(
            status=status,
            category=category,
            staff_id=uuid.UUID(str(staff_id)) if staff_id else None,
            from_date=from_date,
            to_date=to_date,
        )
        repo = ExpenseRepository(info.context.db)
        rows = await repo.list_filtered(**filter_kwargs, skip=skip, limit=limit)
        total = await repo.count_filtered(**filter_kwargs)
        return PaginatedExpenses(
            items=[ExpenseType.from_orm(r) for r in rows],
            page_info=build_page_info(
                total_count=total,
                page=max(1, pagination.page),
                page_size=limit,
            ),
        )

    @strawberry.field
    async def expense(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ExpenseType | None:
        repo = ExpenseRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return ExpenseType.from_orm(obj) if obj else None
