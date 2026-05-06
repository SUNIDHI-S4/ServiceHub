"""Salary mutation inputs."""
from __future__ import annotations

from decimal import Decimal as D

import strawberry

from app.graphql.scalars import Decimal


@strawberry.input
class CreateSalaryInput:
    staff_id: strawberry.ID
    amount: Decimal
    pay_year: int
    pay_month: int
    bonus: Decimal = D("0")
    notes: str | None = None


@strawberry.input
class UpdateSalaryInput:
    amount: Decimal | None = strawberry.UNSET
    bonus: Decimal | None = strawberry.UNSET
    notes: str | None = strawberry.UNSET
