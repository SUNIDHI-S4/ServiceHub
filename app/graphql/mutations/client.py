"""Client mutations."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.client import CreateClientInput, UpdateClientInput
from app.graphql.types.client import ClientType
from app.models.client import Client
from app.repositories.client import ClientRepository


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class ClientMutations:
    @strawberry.mutation
    async def create_client(
        self, info: strawberry.Info, input: CreateClientInput
    ) -> ClientType:
        repo = ClientRepository(info.context.db)
        obj = Client(name=input.name, email=input.email, phone=input.phone)
        obj = await repo.add(obj)
        return ClientType.from_orm(obj)

    @strawberry.mutation
    async def update_client(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: UpdateClientInput,
    ) -> ClientType | None:
        repo = ClientRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return None
        if _is_set(input.name):
            obj.name = input.name
        if _is_set(input.email):
            obj.email = input.email
        if _is_set(input.phone):
            obj.phone = input.phone
        await info.context.db.flush()
        await info.context.db.refresh(obj)
        return ClientType.from_orm(obj)

    @strawberry.mutation
    async def delete_client(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> bool:
        repo = ClientRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        if obj is None:
            return False
        await repo.delete(obj)
        return True
