"""Appointment mutations."""
from __future__ import annotations

import uuid

import strawberry

from app.graphql.inputs.appointment import (
    CreateAppointmentInput,
    UpdateAppointmentInput,
)
from app.graphql.types.appointment import AppointmentType
from app.models.enums import AppointmentStatus
from app.services.appointment import (
    AppointmentConflictError,
    AppointmentNotFoundError,
    AppointmentService,
)
from app.services.billing import BillingService, InvoiceAlreadyExistsError


def _is_set(value):
    return value is not strawberry.UNSET


@strawberry.type
class AppointmentMutations:
    @strawberry.mutation
    async def create_appointment(
        self, info: strawberry.Info, input: CreateAppointmentInput
    ) -> AppointmentType:
        svc = AppointmentService(info.context.db)
        try:
            obj = await svc.create(
                client_id=uuid.UUID(str(input.client_id)),
                staff_id=uuid.UUID(str(input.staff_id)),
                service_id=uuid.UUID(str(input.service_id)),
                scheduled_at=input.scheduled_at,
                notes=input.notes,
            )
        except AppointmentConflictError as exc:
            raise Exception(f"Conflict: {exc}") from exc
        except ValueError as exc:
            raise Exception(str(exc)) from exc
        return AppointmentType.from_orm(obj)

    @strawberry.mutation
    async def update_appointment(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        input: UpdateAppointmentInput,
    ) -> AppointmentType:
        svc = AppointmentService(info.context.db)
        try:
            obj = await svc.update(
                uuid.UUID(str(id)),
                scheduled_at=input.scheduled_at if _is_set(input.scheduled_at) else None,
                status=input.status if _is_set(input.status) else None,
                notes=input.notes if _is_set(input.notes) else None,
            )
        except AppointmentNotFoundError as exc:
            raise Exception(f"Appointment {exc} not found") from exc
        except AppointmentConflictError as exc:
            raise Exception(f"Conflict: {exc}") from exc
        return AppointmentType.from_orm(obj)

    @strawberry.mutation
    async def confirm_appointment(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> AppointmentType:
        svc = AppointmentService(info.context.db)
        try:
            obj = await svc.set_status(
                uuid.UUID(str(id)), AppointmentStatus.CONFIRMED
            )
        except AppointmentNotFoundError as exc:
            raise Exception(f"Appointment {exc} not found") from exc
        return AppointmentType.from_orm(obj)

    @strawberry.mutation
    async def cancel_appointment(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        reason: str | None = None,
    ) -> AppointmentType:
        svc = AppointmentService(info.context.db)
        try:
            obj = await svc.set_status(
                uuid.UUID(str(id)), AppointmentStatus.CANCELLED
            )
            if reason:
                existing_notes = obj.notes or ""
                obj.notes = f"{existing_notes}\n[CANCELLED] {reason}".strip()
                await info.context.db.flush()
                await info.context.db.refresh(obj)
        except AppointmentNotFoundError as exc:
            raise Exception(f"Appointment {exc} not found") from exc
        return AppointmentType.from_orm(obj)

    @strawberry.mutation
    async def complete_appointment(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> AppointmentType:
        """Mark complete and auto-generate an invoice if one does not exist."""
        appt_svc = AppointmentService(info.context.db)
        billing_svc = BillingService(info.context.db)
        try:
            obj = await appt_svc.set_status(
                uuid.UUID(str(id)), AppointmentStatus.COMPLETED
            )
        except AppointmentNotFoundError as exc:
            raise Exception(f"Appointment {exc} not found") from exc

        try:
            await billing_svc.generate_invoice_for_appointment(obj.id)
        except InvoiceAlreadyExistsError:
            # Idempotent completion — leave the existing invoice alone.
            pass

        return AppointmentType.from_orm(obj)

    @strawberry.mutation
    async def delete_appointment(
        self, info: strawberry.Info, id: strawberry.ID
    ) -> bool:
        svc = AppointmentService(info.context.db)
        return await svc.delete(uuid.UUID(str(id)))
