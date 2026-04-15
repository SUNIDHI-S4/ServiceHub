"""SQLAlchemy ORM models for ServiceHub.

Importing this package registers every model with `Base.metadata`, which is
what Alembic reads for autogenerate. Any new model must be imported here.
"""
from app.models.appointment import Appointment
from app.models.base import Base, TimestampMixin
from app.models.client import Client
from app.models.enums import AppointmentStatus, InvoiceStatus, PaymentMethod
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.service import Service
from app.models.staff import Staff

__all__ = [
    "Base",
    "TimestampMixin",
    "Client",
    "Staff",
    "Service",
    "Appointment",
    "Invoice",
    "Payment",
    "AppointmentStatus",
    "InvoiceStatus",
    "PaymentMethod",
]
