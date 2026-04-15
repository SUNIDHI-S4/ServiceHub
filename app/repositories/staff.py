"""Staff repository."""
from __future__ import annotations

from sqlalchemy import select

from app.models.staff import Staff
from app.repositories.base import BaseRepository


class StaffRepository(BaseRepository[Staff]):
    model = Staff

    async def get_by_email(self, email: str) -> Staff | None:
        result = await self.db.execute(select(Staff).where(Staff.email == email))
        return result.scalar_one_or_none()
