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
    is_active: bool = True


@strawberry.input
class UpdateServiceInput:
    name: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    duration_minutes: int | None = strawberry.UNSET
    price: Decimal | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET
