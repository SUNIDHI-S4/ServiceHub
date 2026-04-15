"""Appointment mutation inputs."""
from __future__ import annotations

from datetime import datetime

import strawberry

from app.graphql.types.enums import AppointmentStatusEnum


@strawberry.input
class CreateAppointmentInput:
    client_id: strawberry.ID
    staff_id: strawberry.ID
    service_id: strawberry.ID
    scheduled_at: datetime
    notes: str | None = None


@strawberry.input
class UpdateAppointmentInput:
    scheduled_at: datetime | None = strawberry.UNSET
    status: AppointmentStatusEnum | None = strawberry.UNSET
    notes: str | None = strawberry.UNSET
