"""Salary repository."""
from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import and_, func, select

from app.models.enums import SalaryStatus
from app.models.salary import Salary
from app.repositories.base import BaseRepository


class SalaryRepository(BaseRepository[Salary]):
    model = Salary

    @staticmethod
    def _build_conditions(
        *,
        staff_id: uuid.UUID | None = None,
        status: SalaryStatus | None = None,
        pay_year: int | None = None,
        pay_month: int | None = None,
    ) -> list:
        conditions = []
        if staff_id is not None:
            conditions.append(Salary.staff_id == staff_id)
        if status is not None:
            conditions.append(Salary.status == status)
        if pay_year is not None:
            conditions.append(Salary.pay_year == pay_year)
        if pay_month is not None:
            conditions.append(Salary.pay_month == pay_month)
        return conditions

    async def list_filtered(
        self,
        *,
        staff_id: uuid.UUID | None = None,
        status: SalaryStatus | None = None,
        pay_year: int | None = None,
        pay_month: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Salary]:
        conditions = self._build_conditions(
            staff_id=staff_id, status=status, pay_year=pay_year, pay_month=pay_month,
        )
        stmt = select(Salary)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = (
            stmt.order_by(Salary.pay_year.desc(), Salary.pay_month.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        *,
        staff_id: uuid.UUID | None = None,
        status: SalaryStatus | None = None,
        pay_year: int | None = None,
        pay_month: int | None = None,
    ) -> int:
        conditions = self._build_conditions(
            staff_id=staff_id, status=status, pay_year=pay_year, pay_month=pay_month,
        )
        stmt = select(func.count()).select_from(Salary)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def list_for_staff(self, staff_id: uuid.UUID) -> list[Salary]:
        result = await self.db.execute(
            select(Salary)
            .where(Salary.staff_id == staff_id)
            .order_by(Salary.pay_year.desc(), Salary.pay_month.desc())
        )
        return list(result.scalars().all())

    async def get_for_period(
        self, staff_id: uuid.UUID, pay_year: int, pay_month: int
    ) -> Salary | None:
        result = await self.db.execute(
            select(Salary).where(
                Salary.staff_id == staff_id,
                Salary.pay_year == pay_year,
                Salary.pay_month == pay_month,
            )
        )
        return result.scalar_one_or_none()

    async def total_paid_for_staff(self, staff_id: uuid.UUID) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Salary.amount), 0)).where(
                Salary.staff_id == staff_id,
                Salary.status == SalaryStatus.PAID,
            )
        )
        return Decimal(result.scalar_one())
