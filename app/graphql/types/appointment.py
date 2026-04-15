"""Appointment GraphQL type with nested client/staff/service/invoice resolvers."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import strawberry

from app.graphql.types.enums import AppointmentStatusEnum

if TYPE_CHECKING:
    from app.graphql.types.client import ClientType
    from app.graphql.types.invoice import InvoiceType
    from app.graphql.types.service import ServiceType
    from app.graphql.types.staff import StaffType


@strawberry.type(name="Appointment")
class AppointmentType:
    id: strawberry.ID
    client_id: strawberry.ID
    staff_id: strawberry.ID
    service_id: strawberry.ID
    scheduled_at: datetime
    status: AppointmentStatusEnum
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def client(
        self, info: strawberry.Info
    ) -> Annotated["ClientType", strawberry.lazy("app.graphql.types.client")]:
        from app.graphql.types.client import ClientType
        from app.repositories.client import ClientRepository

        repo = ClientRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(self.client_id)))
        return ClientType.from_orm(obj)

    @strawberry.field
    async def staff_member(
        self, info: strawberry.Info
    ) -> Annotated["StaffType", strawberry.lazy("app.graphql.types.staff")]:
        from app.graphql.types.staff import StaffType
        from app.repositories.staff import StaffRepository

        repo = StaffRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(self.staff_id)))
        return StaffType.from_orm(obj)

    @strawberry.field
    async def service(
        self, info: strawberry.Info
    ) -> Annotated["ServiceType", strawberry.lazy("app.graphql.types.service")]:
        from app.graphql.types.service import ServiceType
        from app.repositories.service import ServiceRepository

        repo = ServiceRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(self.service_id)))
        return ServiceType.from_orm(obj)

    @strawberry.field
    async def invoice(
        self, info: strawberry.Info
    ) -> Annotated["InvoiceType", strawberry.lazy("app.graphql.types.invoice")] | None:
        from app.graphql.types.invoice import InvoiceType
        from app.repositories.billing import BillingRepository

        repo = BillingRepository(info.context.db)
        obj = await repo.get_invoice_by_appointment_id(uuid.UUID(str(self.id)))
        return InvoiceType.from_orm(obj) if obj else None

    @classmethod
    def from_orm(cls, obj) -> "AppointmentType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            client_id=strawberry.ID(str(obj.client_id)),
            staff_id=strawberry.ID(str(obj.staff_id)),
            service_id=strawberry.ID(str(obj.service_id)),
            scheduled_at=obj.scheduled_at,
            status=obj.status,
            notes=obj.notes,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
