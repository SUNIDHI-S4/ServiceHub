"""Billing repository — invoices and payments."""
from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select

from app.models.enums import InvoiceStatus
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.repositories.base import BaseRepository


class BillingRepository(BaseRepository[Invoice]):
    """Handles both invoices and payments; they share a transactional boundary."""

    model = Invoice

    async def list_invoices(
        self,
        *,
        status: InvoiceStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Invoice]:
        stmt = select(Invoice)
        if status is not None:
            stmt = stmt.where(Invoice.status == status)
        stmt = stmt.order_by(Invoice.issued_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_invoice_by_appointment_id(
        self, appointment_id: uuid.UUID
    ) -> Invoice | None:
        result = await self.db.execute(
            select(Invoice).where(Invoice.appointment_id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_payments_for_invoice(
        self, invoice_id: uuid.UUID
    ) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(Payment.paid_at.asc())
        )
        return list(result.scalars().all())

    async def sum_payments_for_invoice(self, invoice_id: uuid.UUID) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.invoice_id == invoice_id
            )
        )
        total = result.scalar_one()
        return Decimal(total)

    async def add_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment
