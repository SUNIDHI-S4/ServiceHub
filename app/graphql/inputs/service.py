"""Service mutation inputs."""
from __future__ import annotations

import strawberry

from app.graphql.scalars import Decimal


@strawberry.input
class CreateServiceInput:
    name: str
    duration_minutes: int
    price: Decimal
    description: str | None = None
    gst_percent: Decimal = Decimal("0")
    bonus: Decimal = Decimal("0")
    is_active: bool = True


@strawberry.input
class UpdateServiceInput:
    name: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    duration_minutes: int | None = strawberry.UNSET
    price: Decimal | None = strawberry.UNSET
    gst_percent: Decimal | None = strawberry.UNSET
    bonus: Decimal | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET
