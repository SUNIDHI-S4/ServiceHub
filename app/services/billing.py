"""Billing business-logic service: invoice generation, payments, status."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import InvoiceStatus, PaymentMethod
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.repositories.appointment import AppointmentRepository
from app.repositories.billing import BillingRepository
from app.repositories.service import ServiceRepository


class InvoiceAlreadyExistsError(Exception):
    pass


class InvoiceNotFoundError(Exception):
    pass


class AppointmentNotFoundError(Exception):
    pass


class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.billing = BillingRepository(db)
        self.appointments = AppointmentRepository(db)
        self.services = ServiceRepository(db)

    async def generate_invoice_for_appointment(
        self,
        appointment_id: uuid.UUID,
        *,
        override_amount: Decimal | None = None,
    ) -> Invoice:
        existing = await self.billing.get_invoice_by_appointment_id(appointment_id)
        if existing is not None:
            raise InvoiceAlreadyExistsError(
                f"Invoice already exists for appointment {appointment_id}"
            )

        appointment = await self.appointments.get_by_id(appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(str(appointment_id))

        if override_amount is not None:
            amount = override_amount
        else:
            service = await self.services.get_by_id(appointment.service_id)
            assert service is not None
            amount = service.price

        invoice = Invoice(
            appointment_id=appointment.id,
            amount=amount,
            status=InvoiceStatus.PENDING,
        )
        return await self.billing.add(invoice)

    async def record_payment(
        self,
        *,
        invoice_id: uuid.UUID,
        amount: Decimal,
        method: PaymentMethod,
    ) -> Payment:
        invoice = await self.billing.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(str(invoice_id))

        payment = Payment(
            invoice_id=invoice.id,
            amount=amount,
            method=method,
        )
        payment = await self.billing.add_payment(payment)
        await self._recompute_invoice_status(invoice)
        return payment

    async def mark_overdue(self, invoice_id: uuid.UUID) -> Invoice:
        invoice = await self.billing.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(str(invoice_id))
        # Only pending invoices can transition to overdue; paid invoices are final.
        if invoice.status == InvoiceStatus.PENDING:
            invoice.status = InvoiceStatus.OVERDUE
            await self.db.flush()
            await self.db.refresh(invoice)
        return invoice

    async def _recompute_invoice_status(self, invoice: Invoice) -> None:
        total_paid = await self.billing.sum_payments_for_invoice(invoice.id)
        if total_paid >= invoice.amount and invoice.status != InvoiceStatus.PAID:
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now(tz=timezone.utc)
            await self.db.flush()
            await self.db.refresh(invoice)
