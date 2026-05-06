"""Expense repository."""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, func, select

from app.models.enums import ExpenseCategory, ExpenseStatus
from app.models.expense import Expense
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    model = Expense

    @staticmethod
    def _build_conditions(
        *,
        status: ExpenseStatus | None = None,
        category: ExpenseCategory | None = None,
        staff_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list:
        conditions = []
        if status is not None:
            conditions.append(Expense.status == status)
        if category is not None:
            conditions.append(Expense.category == category)
        if staff_id is not None:
            conditions.append(Expense.staff_id == staff_id)
        if from_date is not None:
            conditions.append(Expense.expense_date >= from_date)
        if to_date is not None:
            conditions.append(Expense.expense_date <= to_date)
        return conditions

    async def list_filtered(
        self,
        *,
        status: ExpenseStatus | None = None,
        category: ExpenseCategory | None = None,
        staff_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Expense]:
        conditions = self._build_conditions(
            status=status, category=category, staff_id=staff_id,
            from_date=from_date, to_date=to_date,
        )
        stmt = select(Expense)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Expense.expense_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        *,
        status: ExpenseStatus | None = None,
        category: ExpenseCategory | None = None,
        staff_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> int:
        conditions = self._build_conditions(
            status=status, category=category, staff_id=staff_id,
            from_date=from_date, to_date=to_date,
        )
        stmt = select(func.count()).select_from(Expense)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def list_for_staff(self, staff_id: uuid.UUID) -> list[Expense]:
        result = await self.db.execute(
            select(Expense)
            .where(Expense.staff_id == staff_id)
            .order_by(Expense.expense_date.desc())
        )
        return list(result.scalars().all())
