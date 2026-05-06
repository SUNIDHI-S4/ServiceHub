"""Staff mutation inputs."""
from __future__ import annotations

from decimal import Decimal as D

import strawberry

from app.graphql.scalars import Decimal


@strawberry.input
class CreateStaffInput:
    name: str
    email: str
    role: str
    specializations: list[str] = strawberry.field(default_factory=list)
    monthly_salary: Decimal = D("0")


@strawberry.input
class UpdateStaffInput:
    name: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET
    role: str | None = strawberry.UNSET
    specializations: list[str] | None = strawberry.UNSET
    monthly_salary: Decimal | None = strawberry.UNSET
