"""Service mutations."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.service import CreateServiceInput, UpdateServiceInput
from app.graphql.types.service import ServiceType
from app.models.service import Service
from app.repositories.service import ServiceRepository


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class ServiceMutations:
    @strawberry.mutation
    async def create_service(
        self, info: strawberry.Info, input: CreateServiceInput
    ) -> ServiceType:
        repo = ServiceRepository(info.context.db)
        obj = Service(
            name=input.name,
            description=input.description,
            duration_minutes=input.duration_minutes,
            price=input.price,
            is_active=input.is_active,
        )
        obj = await repo.add(obj)
        return ServiceType.from_orm(obj)

    @strawberry.mutation
    async def update_service(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: UpdateServiceInput,
    ) -> ServiceType | None:
        repo = ServiceRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return None
        if _is_set(input.name):
            obj.name = input.name
        if _is_set(input.description):
            obj.description = input.description
        if _is_set(input.duration_minutes):
            obj.duration_minutes = input.duration_minutes
        if _is_set(input.price):
            obj.price = input.price
        if _is_set(input.is_active):
            obj.is_active = input.is_active
        await info.context.db.flush()
        await info.context.db.refresh(obj)
        return ServiceType.from_orm(obj)

    @strawberry.mutation
    async def deactivate_service(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> ServiceType | None:
        """Soft-delete — services retain history via past appointments."""
        repo = ServiceRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return None
        obj.is_active = False
        await info.context.db.flush()
        await info.context.db.refresh(obj)
        return ServiceType.from_orm(obj)
