"""Appointment business-logic service."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.repositories.appointment import AppointmentRepository
from app.repositories.client import ClientRepository
from app.repositories.service import ServiceRepository
from app.repositories.staff import StaffRepository


class AppointmentConflictError(Exception):
    """Raised when a requested appointment overlaps an existing booking."""


class AppointmentNotFoundError(Exception):
    """Raised when an appointment cannot be located."""


class AppointmentService:
    """Encapsulates booking rules so resolvers stay thin."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.appointments = AppointmentRepository(db)
        self.clients = ClientRepository(db)
        self.staff = StaffRepository(db)
        self.services = ServiceRepository(db)

    async def create(
        self,
        *,
        client_id: uuid.UUID,
        staff_id: uuid.UUID,
        service_id: uuid.UUID,
        scheduled_at: datetime,
        notes: str | None,
    ) -> Appointment:
        client = await self.clients.get_by_id(client_id)
        if client is None:
            raise ValueError(f"Client {client_id} not found")
        staff = await self.staff.get_by_id(staff_id)
        if staff is None:
            raise ValueError(f"Staff {staff_id} not found")
        service = await self.services.get_by_id(service_id)
        if service is None:
            raise ValueError(f"Service {service_id} not found")
        if not service.is_active:
            raise ValueError(f"Service {service_id} is inactive")

        conflicts = await self.appointments.find_staff_conflicts(
            staff_id=staff_id,
            scheduled_at=scheduled_at,
            duration_minutes=service.duration_minutes,
        )
        if conflicts:
            raise AppointmentConflictError(
                f"Staff {staff_id} already has an appointment overlapping "
                f"{scheduled_at.isoformat()}"
            )

        appointment = Appointment(
            client_id=client_id,
            staff_id=staff_id,
            service_id=service_id,
            scheduled_at=scheduled_at,
            notes=notes,
            status=AppointmentStatus.PENDING,
        )
        return await self.appointments.add(appointment)

    async def update(
        self,
        appointment_id: uuid.UUID,
        *,
        scheduled_at: datetime | None,
        status: AppointmentStatus | None,
        notes: str | None,
    ) -> Appointment:
        appointment = await self.appointments.get_by_id(appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(str(appointment_id))

        if scheduled_at is not None and scheduled_at != appointment.scheduled_at:
            service = await self.services.get_by_id(appointment.service_id)
            assert service is not None
            conflicts = await self.appointments.find_staff_conflicts(
                staff_id=appointment.staff_id,
                scheduled_at=scheduled_at,
                duration_minutes=service.duration_minutes,
                exclude_appointment_id=appointment.id,
            )
            if conflicts:
                raise AppointmentConflictError(
                    f"Staff already has an appointment overlapping "
                    f"{scheduled_at.isoformat()}"
                )
            appointment.scheduled_at = scheduled_at

        if status is not None:
            appointment.status = status
        if notes is not None:
            appointment.notes = notes

        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    async def set_status(
        self, appointment_id: uuid.UUID, status: AppointmentStatus
    ) -> Appointment:
        appointment = await self.appointments.get_by_id(appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(str(appointment_id))
        appointment.status = status
        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    async def delete(self, appointment_id: uuid.UUID) -> bool:
        appointment = await self.appointments.get_by_id(appointment_id)
        if appointment is None:
            return False
        await self.appointments.delete(appointment)
        return True
