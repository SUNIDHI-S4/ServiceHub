"""Root Strawberry schema — combines Query and Mutation."""
from __future__ import annotations

import strawberry

from app.graphql.mutations import Mutation
from app.graphql.queries import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
