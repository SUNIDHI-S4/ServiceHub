"""Query resolver mixins composed into the root `Query` type."""
import strawberry

from app.graphql.queries.appointment import AppointmentQueries
from app.graphql.queries.billing import BillingQueries
from app.graphql.queries.client import ClientQueries
from app.graphql.queries.service import ServiceQueries
from app.graphql.queries.staff import StaffQueries


@strawberry.type
class Query(
    ClientQueries,
    StaffQueries,
    ServiceQueries,
    AppointmentQueries,
    BillingQueries,
):
    """Root GraphQL Query type, assembled from per-domain mixins."""


__all__ = ["Query"]
