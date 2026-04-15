"""Staff mutation inputs."""
from __future__ import annotations

import strawberry


@strawberry.input
class CreateStaffInput:
    name: str
    email: str
    role: str
    specializations: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateStaffInput:
    name: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET
    role: str | None = strawberry.UNSET
    specializations: list[str] | None = strawberry.UNSET
