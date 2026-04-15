"""Service GraphQL type."""
from __future__ import annotations

from datetime import datetime

import strawberry

from app.graphql.scalars import Decimal


@strawberry.type(name="Service")
class ServiceType:
    id: strawberry.ID
    name: str
    description: str | None
    duration_minutes: int
    price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "ServiceType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            description=obj.description,
            duration_minutes=obj.duration_minutes,
            price=obj.price,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
