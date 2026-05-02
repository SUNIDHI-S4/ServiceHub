"""Strawberry GraphQL output types."""
from app.graphql.types.appointment import AppointmentType
from app.graphql.types.client import ClientType
from app.graphql.types.enums import (
    AppointmentStatusEnum,
    ExpenseCategoryEnum,
    ExpenseStatusEnum,
    InvoiceStatusEnum,
    PaymentMethodEnum,
    SalaryStatusEnum,
)
from app.graphql.types.expense import ExpenseType
from app.graphql.types.invoice import InvoiceType
from app.graphql.types.payment import PaymentType
from app.graphql.types.salary import SalaryType
from app.graphql.types.service import ServiceType
from app.graphql.types.staff import StaffType

__all__ = [
    "AppointmentType",
    "ClientType",
    "ExpenseType",
    "InvoiceType",
    "PaymentType",
    "SalaryType",
    "ServiceType",
    "StaffType",
    "AppointmentStatusEnum",
    "ExpenseCategoryEnum",
    "ExpenseStatusEnum",
    "InvoiceStatusEnum",
    "PaymentMethodEnum",
    "SalaryStatusEnum",
]
