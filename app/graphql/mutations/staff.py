"""Staff mutations."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.staff import CreateStaffInput, UpdateStaffInput
from app.graphql.types.staff import StaffType
from app.models.staff import Staff
from app.repositories.staff import StaffRepository


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class StaffMutations:
    @strawberry.mutation
    async def create_staff(
        self, info: strawberry.Info, input: CreateStaffInput
    ) -> StaffType:
        repo = StaffRepository(info.context.db)
        obj = Staff(
            name=input.name,
            email=input.email,
            role=input.role,
            specializations=list(input.specializations or []),
        )
        obj = await repo.add(obj)
        return StaffType.from_orm(obj)

    @strawberry.mutation
    async def update_staff(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: UpdateStaffInput,
    ) -> StaffType | None:
        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return None
        if _is_set(input.name):
            obj.name = input.name
        if _is_set(input.email):
            obj.email = input.email
        if _is_set(input.role):
            obj.role = input.role
        if _is_set(input.specializations):
            obj.specializations = list(input.specializations or [])
        await info.context.db.flush()
        await info.context.db.refresh(obj)
        return StaffType.from_orm(obj)

    @strawberry.mutation
    async def delete_staff(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> bool:
        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return False
        await repo.delete(obj)
        return True
