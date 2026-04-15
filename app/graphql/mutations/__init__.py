"""Mutation resolver mixins composed into the root `Mutation` type."""
import strawberry

from app.graphql.mutations.appointment import AppointmentMutations
from app.graphql.mutations.billing import BillingMutations
from app.graphql.mutations.client import ClientMutations
from app.graphql.mutations.service import ServiceMutations
from app.graphql.mutations.staff import StaffMutations


@strawberry.type
class Mutation(
    ClientMutations,
    StaffMutations,
    ServiceMutations,
    AppointmentMutations,
    BillingMutations,
):
    """Root GraphQL Mutation type, assembled from per-domain mixins."""


__all__ = ["Mutation"]
