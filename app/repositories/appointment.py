"""Appointment repository including conflict detection."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_, func, select

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.service import Service
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    model = Appointment

    async def list_filtered(
        self,
        *,
        status: AppointmentStatus | None = None,
        client_id: uuid.UUID | None = None,
        staff_id: uuid.UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Appointment]:
        stmt = select(Appointment)
        conditions = []
        if status is not None:
            conditions.append(Appointment.status == status)
        if client_id is not None:
            conditions.append(Appointment.client_id == client_id)
        if staff_id is not None:
            conditions.append(Appointment.staff_id == staff_id)
        if from_date is not None:
            conditions.append(Appointment.scheduled_at >= from_date)
        if to_date is not None:
            conditions.append(Appointment.scheduled_at <= to_date)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Appointment.scheduled_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_for_client(self, client_id: uuid.UUID) -> list[Appointment]:
        result = await self.db.execute(
            select(Appointment)
            .where(Appointment.client_id == client_id)
            .order_by(Appointment.scheduled_at.desc())
        )
        return list(result.scalars().all())

    async def list_for_staff(self, staff_id: uuid.UUID) -> list[Appointment]:
        result = await self.db.execute(
            select(Appointment)
            .where(Appointment.staff_id == staff_id)
            .order_by(Appointment.scheduled_at.desc())
        )
        return list(result.scalars().all())

    async def find_staff_conflicts(
        self,
        *,
        staff_id: uuid.UUID,
        scheduled_at: datetime,
        duration_minutes: int,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> list[Appointment]:
        """Return any existing non-cancelled appointments whose time window
        overlaps [scheduled_at, scheduled_at + duration_minutes) for the
        given staff member.

        Overlap logic uses the service's `duration_minutes` for each
        existing appointment to compute its end time dynamically.
        """
        requested_end = scheduled_at + timedelta(minutes=duration_minutes)

        stmt = (
            select(Appointment)
            .join(Service, Appointment.service_id == Service.id)
            .where(
                Appointment.staff_id == staff_id,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.scheduled_at < requested_end,
                (
                    Appointment.scheduled_at
                    + func.make_interval(0, 0, 0, 0, 0, Service.duration_minutes)
                )
                > scheduled_at,
            )
        )
        if exclude_appointment_id is not None:
            stmt = stmt.where(Appointment.id != exclude_appointment_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
