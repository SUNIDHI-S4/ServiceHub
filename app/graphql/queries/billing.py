"""Billing queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.enums import InvoiceStatusEnum
from app.graphql.types.invoice import InvoiceType
from app.graphql.types.payment import PaymentType
from app.repositories.billing import BillingRepository


@strawberry.type
class BillingQueries:
    @strawberry.field
    async def invoices(
        self,
        info: strawberry.Info,
        status: InvoiceStatusEnum | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[InvoiceType]:
        repo = BillingRepository(info.context.db)
        rows = await repo.list_invoices(status=status, skip=skip, limit=limit)
        return [InvoiceType.from_orm(r) for r in rows]

    @strawberry.field
    async def invoice(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> InvoiceType | None:
        repo = BillingRepository(info.context.db)
        obj = await repo.get_by_id(uuid.UUID(str(id)))
        return InvoiceType.from_orm(obj) if obj else None

    @strawberry.field
    async def payments_for_invoice(
        self, info: strawberry.Info, invoice_id: strawberry.ID
    ) -> list[PaymentType]:
        repo = BillingRepository(info.context.db)
        rows = await repo.get_payments_for_invoice(uuid.UUID(str(invoice_id)))
        return [PaymentType.from_orm(r) for r in rows]
