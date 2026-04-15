"""Billing mutations — invoices and payments."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.billing import CreateInvoiceInput, RecordPaymentInput
from app.graphql.types.invoice import InvoiceType
from app.graphql.types.payment import PaymentType
from app.services.billing import (
    BillingService,
    InvoiceAlreadyExistsError,
    InvoiceNotFoundError,
    AppointmentNotFoundError,
)


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class BillingMutations:
    @strawberry.mutation
    async def create_invoice(
        self, info: strawberry.Info, input: CreateInvoiceInput
    ) -> InvoiceType:
        svc = BillingService(info.context.db)
        override = input.amount if _is_set(input.amount) else None
        try:
            obj = await svc.generate_invoice_for_appointment(
                uuid.UUID(str(input.appointment_id)),
                override_amount=override,
            )
        except InvoiceAlreadyExistsError as exc:
            raise Exception(str(exc)) from exc
        except AppointmentNotFoundError as exc:
            raise Exception(f"Appointment {exc} not found") from exc
        return InvoiceType.from_orm(obj)

    @strawberry.mutation
    async def record_payment(
        self, info: strawberry.Info, input: RecordPaymentInput
    ) -> PaymentType:
        svc = BillingService(info.context.db)
        try:
            obj = await svc.record_payment(
                invoice_id=uuid.UUID(str(input.invoice_id)),
                amount=input.amount,
                method=input.method,
            )
        except InvoiceNotFoundError as exc:
            raise Exception(f"Invoice {exc} not found") from exc
        return PaymentType.from_orm(obj)

    @strawberry.mutation
    async def mark_invoice_overdue(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> InvoiceType:
        svc = BillingService(info.context.db)
        try:
            obj = await svc.mark_overdue(uuid.UUID(str(id)))
        except InvoiceNotFoundError as exc:
            raise Exception(f"Invoice {exc} not found") from exc
        return InvoiceType.from_orm(obj)
