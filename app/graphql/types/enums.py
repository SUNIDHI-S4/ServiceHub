"""Strawberry wrappers around the Python domain enums.

Re-exporting the Python enums via `strawberry.enum` registers them with the
GraphQL schema while keeping a single source of truth for enum values.
"""
from __future__ import annotations

import strawberry

from app.models.enums import (
    AppointmentStatus,
    ExpenseCategory,
    ExpenseStatus,
    InvoiceStatus,
    PaymentMethod,
    SalaryStatus,
)

AppointmentStatusEnum = strawberry.enum(AppointmentStatus, name="AppointmentStatus")
InvoiceStatusEnum = strawberry.enum(InvoiceStatus, name="InvoiceStatus")
PaymentMethodEnum = strawberry.enum(PaymentMethod, name="PaymentMethod")
ExpenseCategoryEnum = strawberry.enum(ExpenseCategory, name="ExpenseCategory")
ExpenseStatusEnum = strawberry.enum(ExpenseStatus, name="ExpenseStatus")
SalaryStatusEnum = strawberry.enum(SalaryStatus, name="SalaryStatus")
