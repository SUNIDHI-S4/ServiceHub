"""Strawberry GraphQL input types."""
from app.graphql.inputs.appointment import (
    CreateAppointmentInput,
    UpdateAppointmentInput,
)
from app.graphql.inputs.billing import (
    CreateInvoiceInput,
    RecordPaymentInput,
)
from app.graphql.inputs.client import CreateClientInput, UpdateClientInput
from app.graphql.inputs.expense import CreateExpenseInput, UpdateExpenseInput
from app.graphql.inputs.salary import CreateSalaryInput, UpdateSalaryInput
from app.graphql.inputs.service import CreateServiceInput, UpdateServiceInput
from app.graphql.inputs.staff import CreateStaffInput, UpdateStaffInput

__all__ = [
    "CreateAppointmentInput",
    "UpdateAppointmentInput",
    "CreateClientInput",
    "UpdateClientInput",
    "CreateExpenseInput",
    "UpdateExpenseInput",
    "CreateSalaryInput",
    "UpdateSalaryInput",
    "CreateServiceInput",
    "UpdateServiceInput",
    "CreateStaffInput",
    "UpdateStaffInput",
    "CreateInvoiceInput",
    "RecordPaymentInput",
]
