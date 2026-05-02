"""Expense queries."""
from __future__ import annotations

import uuid
from datetime import date

import strawberry

from app.graphql.types.enums import ExpenseCategoryEnum, ExpenseStatusEnum
from app.graphql.types.expense import ExpenseType
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
        skip: int = 0,
        limit: int = 50,
    ) -> list[ExpenseType]:
        repo = ExpenseRepository(info.context.db)
        rows = await repo.list_filtered(
            status=status,
            category=category,
            staff_id=uuid.UUID(str(staff_id)) if staff_id else None,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit,
        )
        return [ExpenseType.from_orm(r) for r in rows]

    @strawberry.field
    async def expense(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ExpenseType | None:
        repo = ExpenseRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return ExpenseType.from_orm(obj) if obj else None
