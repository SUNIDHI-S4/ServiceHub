"""Concrete paginated response types — one per domain.

Strawberry does not support generic @strawberry.type classes, so each
paginated response must be a concrete class with explicit type annotations.
"""
from __future__ import annotations

import strawberry

from app.graphql.types.appointment import AppointmentType
from app.graphql.types.client import ClientType
from app.graphql.types.expense import ExpenseType
from app.graphql.types.invoice import InvoiceType
from app.graphql.types.pagination import PageInfo
from app.graphql.types.payment import PaymentType
from app.graphql.types.salary import SalaryType
from app.graphql.types.service import ServiceType
from app.graphql.types.staff import StaffType


@strawberry.type
class PaginatedClients:
    items: list[ClientType]
    page_info: PageInfo


@strawberry.type
class PaginatedStaff:
    items: list[StaffType]
    page_info: PageInfo


@strawberry.type
class PaginatedServices:
    items: list[ServiceType]
    page_info: PageInfo


@strawberry.type
class PaginatedAppointments:
    items: list[AppointmentType]
    page_info: PageInfo


@strawberry.type
class PaginatedInvoices:
    items: list[InvoiceType]
    page_info: PageInfo


@strawberry.type
class PaginatedPayments:
    items: list[PaymentType]
    page_info: PageInfo


@strawberry.type
class PaginatedExpenses:
    items: list[ExpenseType]
    page_info: PageInfo


@strawberry.type
class PaginatedSalaries:
    items: list[SalaryType]
    page_info: PageInfo
