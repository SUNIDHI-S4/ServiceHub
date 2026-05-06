"""Billing queries."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.types.enums import InvoiceStatusEnum
from app.graphql.types.invoice import InvoiceType
from app.graphql.types.paginated import PaginatedInvoices, PaginatedPayments
from app.graphql.types.pagination import (
    PaginationInput,
    build_page_info,
    pagination_to_offset,
)
from app.graphql.types.payment import PaymentType
from app.repositories.billing import BillingRepository


@strawberry.type
class BillingQueries:
    @strawberry.field
    async def invoices(
        self,
        info: strawberry.Info,
        status: InvoiceStatusEnum | None = None,
        pagination: PaginationInput | None = None,
    ) -> PaginatedInvoices:
        pagination = pagination or PaginationInput()
        skip, limit = pagination_to_offset(pagination)
        repo = BillingRepository(info.context.db)
        rows = await repo.list_invoices(status=status, skip=skip, limit=limit)
        total = await repo.count_invoices(status=status)
        return PaginatedInvoices(
            items=[InvoiceType.from_orm(r) for r in rows],
            page_info=build_page_info(
                total_count=total,
                page=max(1, pagination.page),
                page_size=limit,
            ),
        )

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
