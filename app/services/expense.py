"""Expense business-logic service."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ExpenseCategory, ExpenseStatus
from app.models.expense import Expense
from app.repositories.expense import ExpenseRepository
from app.repositories.staff import StaffRepository


class ExpenseNotFoundError(Exception):
    pass


class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expenses = ExpenseRepository(db)
        self.staff = StaffRepository(db)

    async def create(
        self,
        *,
        description: str,
        amount: Decimal,
        category: ExpenseCategory,
        expense_date: date,
        staff_id: uuid.UUID | None = None,
        receipt_url: str | None = None,
        notes: str | None = None,
    ) -> Expense:
        if staff_id is not None:
            staff = await self.staff.get_by_id(staff_id)
            if staff is None:
                raise ValueError(f"Staff {staff_id} not found")

        expense = Expense(
            description=description,
            amount=amount,
            category=category,
            expense_date=expense_date,
            staff_id=staff_id,
            receipt_url=receipt_url,
            notes=notes,
            status=ExpenseStatus.PENDING,
        )
        return await self.expenses.add(expense)

    async def approve(self, expense_id: uuid.UUID) -> Expense:
        expense = await self.expenses.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(str(expense_id))
        if expense.status != ExpenseStatus.PENDING:
            raise ValueError(
                f"Cannot approve expense in {expense.status.value} status"
            )
        expense.status = ExpenseStatus.APPROVED
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def reject(self, expense_id: uuid.UUID, reason: str | None = None) -> Expense:
        expense = await self.expenses.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(str(expense_id))
        if expense.status != ExpenseStatus.PENDING:
            raise ValueError(
                f"Cannot reject expense in {expense.status.value} status"
            )
        expense.status = ExpenseStatus.REJECTED
        if reason:
            existing = expense.notes or ""
            expense.notes = f"{existing}\n[REJECTED] {reason}".strip()
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def reimburse(self, expense_id: uuid.UUID) -> Expense:
        expense = await self.expenses.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(str(expense_id))
        if expense.status != ExpenseStatus.APPROVED:
            raise ValueError(
                f"Only approved expenses can be reimbursed (current: {expense.status.value})"
            )
        expense.status = ExpenseStatus.REIMBURSED
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def delete(self, expense_id: uuid.UUID) -> bool:
        expense = await self.expenses.get_by_id(expense_id)
        if expense is None:
            return False
        await self.expenses.delete(expense)
        return True
