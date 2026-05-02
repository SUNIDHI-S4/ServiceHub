"""Expense ORM model — tracks business expenses optionally tied to a staff member."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import ExpenseCategory, ExpenseStatus

if TYPE_CHECKING:
    from app.models.staff import Staff


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[ExpenseCategory] = mapped_column(
        SAEnum(ExpenseCategory, name="expense_category"), nullable=False
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ExpenseStatus] = mapped_column(
        SAEnum(ExpenseStatus, name="expense_status"),
        nullable=False,
        default=ExpenseStatus.PENDING,
        server_default=ExpenseStatus.PENDING.value,
    )
    # Optional — an expense may be incurred by a specific staff member
    # (e.g. travel reimbursement) or be a general business expense (rent).
    staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    receipt_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    staff_member: Mapped["Staff | None"] = relationship(
        back_populates="expenses",
    )
