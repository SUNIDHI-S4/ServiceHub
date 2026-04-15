"""Custom Strawberry scalars for ServiceHub.

`Decimal` is serialized as a string to preserve precision (JSON numbers are
double-precision floats in many clients, which corrupts currency values).
"""
from __future__ import annotations

from decimal import Decimal as PyDecimal
from typing import NewType

import strawberry

Decimal = strawberry.scalar(
    NewType("Decimal", PyDecimal),
    serialize=lambda v: str(v),
    parse_value=lambda v: PyDecimal(str(v)),
    description="Arbitrary-precision decimal, serialized as a string.",
)
