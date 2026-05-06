"""Salary business-logic service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SalaryStatus
from app.models.salary import Salary
from app.repositories.salary import SalaryRepository
from app.repositories.staff import StaffRepository


class SalaryNotFoundError(Exception):
    pass


class DuplicateSalaryError(Exception):
    pass


class SalaryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.salaries = SalaryRepository(db)
        self.staff = StaffRepository(db)

    async def create(
        self,
        *,
        staff_id: uuid.UUID,
        amount: Decimal,
        pay_year: int,
        pay_month: int,
        bonus: Decimal = Decimal("0"),
        notes: str | None = None,
    ) -> Salary:
        staff = await self.staff.get_by_id(staff_id)
        if staff is None:
            raise ValueError(f"Staff {staff_id} not found")

        if not 1 <= pay_month <= 12:
            raise ValueError(f"pay_month must be 1-12, got {pay_month}")

        existing = await self.salaries.get_for_period(staff_id, pay_year, pay_month)
        if existing is not None:
            raise DuplicateSalaryError(
                f"Salary already exists for staff {staff_id} "
                f"for {pay_year}-{pay_month:02d}"
            )

        salary = Salary(
            staff_id=staff_id,
            amount=amount,
            bonus=bonus,
            pay_year=pay_year,
            pay_month=pay_month,
            notes=notes,
            status=SalaryStatus.PENDING,
        )
        return await self.salaries.add(salary)

    async def mark_paid(self, salary_id: uuid.UUID) -> Salary:
        salary = await self.salaries.get_by_id(salary_id)
        if salary is None:
            raise SalaryNotFoundError(str(salary_id))
        if salary.status == SalaryStatus.PAID:
            return salary  # idempotent
        if salary.status == SalaryStatus.CANCELLED:
            raise ValueError("Cannot pay a cancelled salary")
        salary.status = SalaryStatus.PAID
        salary.paid_at = datetime.now(tz=timezone.utc)
        await self.db.flush()
        await self.db.refresh(salary)
        return salary

    async def cancel(self, salary_id: uuid.UUID) -> Salary:
        salary = await self.salaries.get_by_id(salary_id)
        if salary is None:
            raise SalaryNotFoundError(str(salary_id))
        if salary.status == SalaryStatus.PAID:
            raise ValueError("Cannot cancel a salary that has already been paid")
        salary.status = SalaryStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(salary)
        return salary

    async def delete(self, salary_id: uuid.UUID) -> bool:
        salary = await self.salaries.get_by_id(salary_id)
        if salary is None:
            return False
        await self.salaries.delete(salary)
        return True
