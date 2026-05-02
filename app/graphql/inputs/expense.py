"""Expense mutation inputs."""
from __future__ import annotations

from datetime import date

import strawberry

from app.graphql.scalars import Decimal
from app.graphql.types.enums import ExpenseCategoryEnum, ExpenseStatusEnum


@strawberry.input
class CreateExpenseInput:
    description: str
    amount: Decimal
    category: ExpenseCategoryEnum
    expense_date: date
    staff_id: strawberry.ID | None = None
    receipt_url: str | None = None
    notes: str | None = None


@strawberry.input
class UpdateExpenseInput:
    description: str | None = strawberry.UNSET
    amount: Decimal | None = strawberry.UNSET
    category: ExpenseCategoryEnum | None = strawberry.UNSET
    expense_date: date | None = strawberry.UNSET
    staff_id: strawberry.ID | None = strawberry.UNSET
    receipt_url: str | None = strawberry.UNSET
    notes: str | None = strawberry.UNSET
