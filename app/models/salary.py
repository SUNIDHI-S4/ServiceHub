"""Salary ORM model — tracks monthly salary disbursements per staff member."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import SalaryStatus

if TYPE_CHECKING:
    from app.models.staff import Staff


class Salary(Base, TimestampMixin):
    __tablename__ = "salaries"
    __table_args__ = (
        # One salary record per staff member per pay period (year + month).
        UniqueConstraint("staff_id", "pay_year", "pay_month", name="uq_staff_pay_period"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    staff_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    bonus: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0, server_default="0"
    )
    pay_year: Mapped[int] = mapped_column(Integer, nullable=False)
    pay_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–12
    status: Mapped[SalaryStatus] = mapped_column(
        SAEnum(SalaryStatus, name="salary_status"),
        nullable=False,
        default=SalaryStatus.PENDING,
        server_default=SalaryStatus.PENDING.value,
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    staff_member: Mapped["Staff"] = relationship(
        back_populates="salaries",
    )
