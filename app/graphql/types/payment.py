"""Payment GraphQL type."""
from __future__ import annotations

from datetime import datetime

import strawberry

from app.graphql.scalars import Decimal
from app.graphql.types.enums import PaymentMethodEnum


@strawberry.type(name="Payment")
class PaymentType:
    id: strawberry.ID
    invoice_id: strawberry.ID
    amount: Decimal
    method: PaymentMethodEnum
    paid_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "PaymentType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            invoice_id=strawberry.ID(str(obj.invoice_id)),
            amount=obj.amount,
            method=obj.method,
            paid_at=obj.paid_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
