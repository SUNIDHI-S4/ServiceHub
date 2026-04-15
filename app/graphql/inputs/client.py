"""Client mutation inputs."""
from __future__ import annotations

import strawberry


@strawberry.input
class CreateClientInput:
    name: str
    email: str
    phone: str | None = None


@strawberry.input
class UpdateClientInput:
    name: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET
    phone: str | None = strawberry.UNSET
