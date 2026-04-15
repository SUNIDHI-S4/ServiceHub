"""Invoice GraphQL type."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import strawberry

from app.graphql.scalars import Decimal
from app.graphql.types.enums import InvoiceStatusEnum

if TYPE_CHECKING:
    from app.graphql.types.appointment import AppointmentType
    from app.graphql.types.payment import PaymentType


@strawberry.type(name="Invoice")
class InvoiceType:
    id: strawberry.ID
    appointment_id: strawberry.ID
    amount: Decimal
    status: InvoiceStatusEnum
    issued_at: datetime
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def appointment(
        self, info: strawberry.Info
    ) -> Annotated["AppointmentType", strawberry.lazy("app.graphql.types.appointment")]:
        from app.graphql.types.appointment import AppointmentType
        from app.repositories.appointment import AppointmentRepository

        repo = AppointmentRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(self.appointment_id)))
        return AppointmentType.from_orm(obj)

    @strawberry.field
    async def payments(
        self, info: strawberry.Info
    ) -> list[Annotated["PaymentType", strawberry.lazy("app.graphql.types.payment")]]:
        from app.graphql.types.payment import PaymentType
        from app.repositories.billing import BillingRepository

        repo = BillingRepository(info.context.db)
        rows = await repo.get_payments_for_invoice(uuid.UUID(str(self.id)))
        return [PaymentType.from_orm(r) for r in rows]

    @strawberry.field
    async def amount_paid(self, info: strawberry.Info) -> Decimal:
        from app.repositories.billing import BillingRepository

        repo = BillingRepository(info.context.db)
        return await repo.sum_payments_for_invoice(uuid.UUID(str(self.id)))

    @classmethod
    def from_orm(cls, obj) -> "InvoiceType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            appointment_id=strawberry.ID(str(obj.appointment_id)),
            amount=obj.amount,
            status=obj.status,
            issued_at=obj.issued_at,
            paid_at=obj.paid_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
