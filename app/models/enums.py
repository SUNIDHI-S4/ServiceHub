"""Domain enums shared between ORM models and GraphQL types."""
from __future__ import annotations

import enum


class AppointmentStatus(str, enum.Enum):
    """Lifecycle states for an appointment."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class InvoiceStatus(str, enum.Enum):
    """Lifecycle states for an invoice."""

    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class PaymentMethod(str, enum.Enum):
    """Accepted payment methods."""

    CASH = "CASH"
    CARD = "CARD"
    ONLINE = "ONLINE"
