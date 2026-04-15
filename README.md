# ServiceHub

A production-ready GraphQL backend for service-based businesses (salons, legal
firms, consultancies). Handles clients, staff, services, appointments, and
billing (invoices + payments) on a single coherent API.

## Stack

- **Python** 3.11+
- **FastAPI** — HTTP framework
- **Strawberry GraphQL** — schema-first (type-annotated) GraphQL
- **SQLAlchemy 2.x (async)** + **asyncpg** — ORM and DB driver
- **PostgreSQL** (Supabase) — database
- **Alembic** — schema migrations
- **Uvicorn** — ASGI server

## Project layout

```
app/
  main.py                 FastAPI app, CORS, /graphql, /health
  config.py               Pydantic settings loaded from .env
  database.py             Async engine + request-scoped session dependency
  models/                 SQLAlchemy ORM models (Client, Staff, Service,
                          Appointment, Invoice, Payment)
  repositories/           Pure DB access per aggregate
  services/               Business logic (appointment conflict checks,
                          invoice generation, payment status transitions)
  graphql/
    scalars.py            Decimal scalar
    context.py            FastAPI -> Strawberry context bridge
    schema.py             Root schema
    types/                @strawberry.type output definitions
    inputs/               @strawberry.input mutation inputs
    queries/              Query resolvers (one mixin per domain)
    mutations/            Mutation resolvers (one mixin per domain)
  migrations/             Alembic migration scripts
```

## Setup

1. Activate the virtualenv and install dependencies:

   ```powershell
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your Supabase credentials. For
   development use port `5432` (direct connection). For production use port
   `6543` (PgBouncer) and set `DATABASE_POOL_SIZE=1`.

3. Generate and apply the initial migration:

   ```powershell
   alembic revision --autogenerate -m "initial_schema"
   alembic upgrade head
   ```

   Review the generated migration before applying — Alembic occasionally
   needs manual fixes for PostgreSQL-specific types (e.g. `ARRAY`).

4. Run the server:

   ```powershell
   uvicorn app.main:app --reload
   ```

5. Open GraphiQL at <http://localhost:8000/graphql> and the health check at
   <http://localhost:8000/health>.

## Example operations

**Create a client:**

```graphql
mutation {
  createClient(input: {
    name: "Jane Doe",
    email: "jane@example.com",
    phone: "+1-555-0123"
  }) {
    id
    name
  }
}
```

**Book an appointment:**

```graphql
mutation {
  createAppointment(input: {
    clientId: "…",
    staffId: "…",
    serviceId: "…",
    scheduledAt: "2026-05-01T14:00:00Z"
  }) {
    id
    status
    service { name price }
  }
}
```

**Complete + auto-invoice:**

```graphql
mutation {
  completeAppointment(id: "…") {
    id
    status
    invoice { id amount status }
  }
}
```

**Record a (partial) payment:**

```graphql
mutation {
  recordPayment(input: {
    invoiceId: "…",
    amount: "50.00",
    method: CASH
  }) {
    id
    amount
  }
}
```

When cumulative payments reach the invoice amount, the invoice transitions
to `PAID` automatically and `paidAt` is set.

## Architectural notes

- **Three-layer separation.** Resolvers are thin: they call services, which
  call repositories. Business rules are independently testable without
  GraphQL.
- **Transaction boundary at the request.** Repositories `flush()`; the
  `get_db` dependency owns the single `commit()` per request, so multi-step
  mutations roll back atomically on error.
- **`expire_on_commit=False`.** Required for async SQLAlchemy to avoid
  `MissingGreenlet` when touching attributes post-commit.
- **Decimal for money.** Every monetary field is `Numeric(10, 2)` in the DB
  and `Decimal` in Python. The GraphQL scalar serializes to a string.
- **UUID primary keys.** Non-sequential, safe to expose in URLs and emails.
- **Hard conflict constraint.** `UniqueConstraint(staff_id, scheduled_at)`
  stops double-booking even under a race; the service layer adds overlap
  checking that considers service duration.
