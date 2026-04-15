"""Appointment queries."""
from __future__ import annotations

import uuid
from datetime import datetime

import strawberry

from app.graphql.types.appointment import AppointmentType
from app.graphql.types.enums import AppointmentStatusEnum
from app.repositories.appointment import AppointmentRepository


@strawberry.type
class AppointmentQueries:
    @strawberry.field
    async def appointments(
        self,
        info: strawberry.Info,
        status: AppointmentStatusEnum | None = None,
        client_id: strawberry.ID | None = None,
        staff_id: strawberry.ID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AppointmentType]:
        repo = AppointmentRepository(info.context.db)
        rows = await repo.list_filtered(
            status=status,
            client_id=uuid.UUID(str(client_id)) if client_id else None,
            staff_id=uuid.UUID(str(staff_id)) if staff_id else None,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit,
        )
        return [AppointmentType.from_orm(r) for r in rows]

    @strawberry.field
    async def appointment(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> AppointmentType | None:
        repo = AppointmentRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return AppointmentType.from_orm(obj) if obj else None
