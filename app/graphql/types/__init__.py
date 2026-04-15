"""Strawberry GraphQL output types."""
from app.graphql.types.appointment import AppointmentType
from app.graphql.types.client import ClientType
from app.graphql.types.enums import (
    AppointmentStatusEnum,
    InvoiceStatusEnum,
    PaymentMethodEnum,
)
from app.graphql.types.invoice import InvoiceType
from app.graphql.types.payment import PaymentType
from app.graphql.types.service import ServiceType
from app.graphql.types.staff import StaffType

__all__ = [
    "AppointmentType",
    "ClientType",
    "InvoiceType",
    "PaymentType",
    "ServiceType",
    "StaffType",
    "AppointmentStatusEnum",
    "InvoiceStatusEnum",
    "PaymentMethodEnum",
]
