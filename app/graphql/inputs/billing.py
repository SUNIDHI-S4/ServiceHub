"""Billing mutation inputs."""
from __future__ import annotations

import strawberry

from app.graphql.scalars import Decimal
from app.graphql.types.enums import PaymentMethodEnum


@strawberry.input
class CreateInvoiceInput:
    appointment_id: strawberry.ID
    # If omitted, the billing service derives the amount from the service price.
    amount: Decimal | None = strawberry.UNSET


@strawberry.input
class RecordPaymentInput:
    invoice_id: strawberry.ID
    amount: Decimal
    method: PaymentMethodEnum
