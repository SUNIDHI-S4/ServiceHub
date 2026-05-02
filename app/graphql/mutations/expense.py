"""Expense mutations."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.expense import CreateExpenseInput, UpdateExpenseInput
from app.graphql.types.expense import ExpenseType
from app.repositories.expense import ExpenseRepository
from app.services.expense import ExpenseNotFoundError, ExpenseService


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class ExpenseMutations:
    @strawberry.mutation
    async def create_expense(
        self, info: strawberry.Info, input: CreateExpenseInput
    ) -> ExpenseType:
        svc = ExpenseService(info.context.db)
        try:
            obj = await svc.create(
                description=input.description,
                amount=input.amount,
                category=input.category,
                expense_date=input.expense_date,
                staff_id=uuid.UUID(str(input.staff_id)) if input.staff_id else None,
                receipt_url=input.receipt_url,
                notes=input.notes,
            )
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return ExpenseType.from_orm(obj)

    @strawberry.mutation
    async def update_expense(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: UpdateExpenseInput,
    ) -> ExpenseType | None:
        repo = ExpenseRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return None
        if _is_set(input.description):
            obj.description = input.description
        if _is_set(input.amount):
            obj.amount = input.amount
        if _is_set(input.category):
            obj.category = input.category
        if _is_set(input.expense_date):
            obj.expense_date = input.expense_date
        if _is_set(input.staff_id):
            obj.staff_id = uuid.UUID(str(input.staff_id)) if input.staff_id else None
        if _is_set(input.receipt_url):
            obj.receipt_url = input.receipt_url
        if _is_set(input.notes):
            obj.notes = input.notes
        await info.context.db.flush()
        await info.context.db.refresh(obj)
        return ExpenseType.from_orm(obj)

    @strawberry.mutation
    async def approve_expense(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ExpenseType:
        svc = ExpenseService(info.context.db)
        try:
            obj = await svc.approve(uuid.UUID(str(id)))
        except ExpenseNotFoundError as exc:
            raise Exception(f"Expense {exc} not found") from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return ExpenseType.from_orm(obj)

    @strawberry.mutation
    async def reject_expense(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        reason: str | None = None,
    ) -> ExpenseType:
        svc = ExpenseService(info.context.db)
        try:
            obj = await svc.reject(uuid.UUID(str(id)), reason=reason)
        except ExpenseNotFoundError as exc:
            raise Exception(f"Expense {exc} not found") from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return ExpenseType.from_orm(obj)

    @strawberry.mutation
    async def reimburse_expense(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ExpenseType:
        svc = ExpenseService(info.context.db)
        try:
            obj = await svc.reimburse(uuid.UUID(str(id)))
        except ExpenseNotFoundError as exc:
            raise Exception(f"Expense {exc} not found") from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return ExpenseType.from_orm(obj)

    @strawberry.mutation
    async def delete_expense(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> bool:
        svc = ExpenseService(info.context.db)
        return await svc.delete(uuid.UUID(str(id)))
