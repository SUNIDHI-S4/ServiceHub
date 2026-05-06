"""Service GraphQL type."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal as D

import strawberry

from app.graphql.scalars import Decimal


@strawberry.type(name="Service")
class ServiceType:
    id: strawberry.ID
    name: str
    description: str | None
    duration_minutes: int
    price: Decimal
    gst_percent: Decimal
    bonus: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    def gst_amount(self) -> Decimal:
        """GST computed from price: price * gst_percent / 100."""
        return (D(str(self.price)) * D(str(self.gst_percent)) / D("100")).quantize(D("0.01"))

    @strawberry.field
    def total_price(self) -> Decimal:
        """price + GST + bonus."""
        gst = D(str(self.price)) * D(str(self.gst_percent)) / D("100")
        return (D(str(self.price)) + gst + D(str(self.bonus))).quantize(D("0.01"))

    @classmethod
    def from_orm(cls, obj) -> "ServiceType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            description=obj.description,
            duration_minutes=obj.duration_minutes,
            price=obj.price,
            gst_percent=obj.gst_percent,
            bonus=obj.bonus,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
