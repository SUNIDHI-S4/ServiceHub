"""Salary GraphQL type."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import strawberry

from app.graphql.scalars import Decimal
from app.graphql.types.enums import SalaryStatusEnum

if TYPE_CHECKING:
    from app.graphql.types.staff import StaffType


@strawberry.type(name="Salary")
class SalaryType:
    id: strawberry.ID
    staff_id: strawberry.ID
    amount: Decimal
    pay_year: int
    pay_month: int
    status: SalaryStatusEnum
    paid_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def staff_member(
        self, info: strawberry.Info
    ) -> Annotated["StaffType", strawberry.lazy("app.graphql.types.staff")]:
        from app.graphql.types.staff import StaffType
        from app.repositories.staff import StaffRepository

        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(self.staff_id)))
        return StaffType.from_orm(obj)

    @classmethod
    def from_orm(cls, obj) -> "SalaryType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            staff_id=strawberry.ID(str(obj.staff_id)),
            amount=obj.amount,
            pay_year=obj.pay_year,
            pay_month=obj.pay_month,
            status=obj.status,
            paid_at=obj.paid_at,
            notes=obj.notes,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
