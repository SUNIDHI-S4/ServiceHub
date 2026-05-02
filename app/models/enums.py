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


class ExpenseCategory(str, enum.Enum):
    """Categories for business expenses."""

    SUPPLIES = "SUPPLIES"
    EQUIPMENT = "EQUIPMENT"
    RENT = "RENT"
    UTILITIES = "UTILITIES"
    MARKETING = "MARKETING"
    TRAVEL = "TRAVEL"
    TRAINING = "TRAINING"
    MAINTENANCE = "MAINTENANCE"
    OTHER = "OTHER"


class ExpenseStatus(str, enum.Enum):
    """Lifecycle states for an expense claim."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REIMBURSED = "REIMBURSED"


class SalaryStatus(str, enum.Enum):
    """Lifecycle states for a salary disbursement."""

    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
