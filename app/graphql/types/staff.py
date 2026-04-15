"""Staff GraphQL type."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import strawberry

if TYPE_CHECKING:
    from app.graphql.types.appointment import AppointmentType


@strawberry.type(name="Staff")
class StaffType:
    id: strawberry.ID
    name: str
    email: str
    role: str
    specializations: list[str]
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def appointments(
        self, info: strawberry.Info
    ) -> list[Annotated["AppointmentType", strawberry.lazy("app.graphql.types.appointment")]]:
        from app.graphql.types.appointment import AppointmentType
        from app.repositories.appointment import AppointmentRepository

        repo = AppointmentRepository(info.context.db)
        rows = await repo.list_for_staff(uuid.UUID(str(self.id)))
        return [AppointmentType.from_orm(r) for r in rows]

    @classmethod
    def from_orm(cls, obj) -> "StaffType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            email=obj.email,
            role=obj.role,
            specializations=list(obj.specializations or []),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
