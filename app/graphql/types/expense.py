"""Expense GraphQL type."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated

import strawberry

from app.graphql.scalars import Decimal
from app.graphql.types.enums import ExpenseCategoryEnum, ExpenseStatusEnum

if TYPE_CHECKING:
    from app.graphql.types.staff import StaffType


@strawberry.type(name="Expense")
class ExpenseType:
    id: strawberry.ID
    description: str
    amount: Decimal
    category: ExpenseCategoryEnum
    expense_date: date
    status: ExpenseStatusEnum
    staff_id: strawberry.ID | None
    receipt_url: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def staff_member(
        self, info: strawberry.Info
    ) -> Annotated["StaffType", strawberry.lazy("app.graphql.types.staff")] | None:
        if self.staff_id is None:
            return None
        from app.graphql.types.staff import StaffType
        from app.repositories.staff import StaffRepository

        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(self.staff_id)))
        return StaffType.from_orm(obj) if obj else None

    @classmethod
    def from_orm(cls, obj) -> "ExpenseType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            description=obj.description,
            amount=obj.amount,
            category=obj.category,
            expense_date=obj.expense_date,
            status=obj.status,
            staff_id=strawberry.ID(str(obj.staff_id)) if obj.staff_id else None,
            receipt_url=obj.receipt_url,
            notes=obj.notes,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
