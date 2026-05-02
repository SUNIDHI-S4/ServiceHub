"""Salary mutations."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.salary import CreateSalaryInput, UpdateSalaryInput
from app.graphql.types.salary import SalaryType
from app.repositories.salary import SalaryRepository
from app.services.salary import (
    DuplicateSalaryError,
    SalaryNotFoundError,
    SalaryService,
)


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class SalaryMutations:
    @strawberry.mutation
    async def create_salary(
        self, info: strawberry.Info, input: CreateSalaryInput
    ) -> SalaryType:
        svc = SalaryService(info.context.db)
        try:
            obj = await svc.create(
                staff_id=uuid.UUID(str(input.staff_id)),
                amount=input.amount,
                pay_year=input.pay_year,
                pay_month=input.pay_month,
                notes=input.notes,
            )
        except DuplicateSalaryError as exc:
            raise Exception(str(exc)) from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return SalaryType.from_orm(obj)

    @strawberry.mutation
    async def update_salary(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: UpdateSalaryInput,
    ) -> SalaryType | None:
        repo = SalaryRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return None
        if _is_set(input.amount):
            obj.amount = input.amount
        if _is_set(input.notes):
            obj.notes = input.notes
        await info.context.db.flush()
        await info.context.db.refresh(obj)
        return SalaryType.from_orm(obj)

    @strawberry.mutation
    async def mark_salary_paid(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> SalaryType:
        svc = SalaryService(info.context.db)
        try:
            obj = await svc.mark_paid(uuid.UUID(str(id)))
        except SalaryNotFoundError as exc:
            raise Exception(f"Salary {exc} not found") from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return SalaryType.from_orm(obj)

    @strawberry.mutation
    async def cancel_salary(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> SalaryType:
        svc = SalaryService(info.context.db)
        try:
            obj = await svc.cancel(uuid.UUID(str(id)))
        except SalaryNotFoundError as exc:
            raise Exception(f"Salary {exc} not found") from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return SalaryType.from_orm(obj)

    @strawberry.mutation
    async def delete_salary(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> bool:
        svc = SalaryService(info.context.db)
        return await svc.delete(uuid.UUID(str(id)))
