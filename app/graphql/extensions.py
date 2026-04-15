"""Custom Strawberry schema extensions."""
from __future__ import annotations

import inspect
from typing import Any

from strawberry.extensions import SchemaExtension


class SerializeDatabaseAccess(SchemaExtension):
    """Serialize every resolver against the request-scoped session.

    Strawberry (via graphql-core) resolves sibling fields concurrently with
    `asyncio.gather`. A SQLAlchemy `AsyncSession` cannot be used from two
    tasks at once — the second one raises
    `InvalidRequestError: This session is provisioning a new connection;
    concurrent operations are not permitted`.

    Holding `info.context.db_lock` around each resolver keeps the session
    safe while preserving the single-transaction-per-request guarantee that
    makes multi-step mutations (e.g. `completeAppointment`) atomic.
    """

    async def resolve(
        self,
        _next,
        root: Any,
        info,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        lock = getattr(info.context, "db_lock", None)
        if lock is None:
            # Subscription / non-DB context — pass through.
            result = _next(root, info, *args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result

        async with lock:
            result = _next(root, info, *args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
