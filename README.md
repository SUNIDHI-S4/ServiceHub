# ServiceHub

A production-ready GraphQL backend for service-based businesses — salons,
legal firms, consultancies, clinics, and anything else that books people
into time slots and bills for it. Built on FastAPI + Strawberry + async
SQLAlchemy + PostgreSQL (Supabase).

One coherent GraphQL API covers the full lifecycle: clients, staff,
services, appointments, and billing (invoices and payments).

---

## Features

- **GraphQL-first.** A single `/graphql` endpoint with full introspection
  and the built-in GraphiQL explorer.
- **Five domains, one schema.** Clients, Staff, Services, Appointments,
  Billing — each with full CRUD, filters, and nested resolvers.
- **Smart scheduling.** Hard DB-level uniqueness on `(staff_id,
  scheduled_at)` plus duration-aware overlap detection in the service
  layer prevents double-booking under any race condition.
- **Automatic billing.** Completing an appointment auto-generates an
  invoice from the service price. Recording payments auto-transitions
  the invoice to `PAID` once the cumulative total is reached.
- **Partial payments.** An invoice can have many payments with mixed
  methods (cash + card + online). The service layer keeps the running
  total and the status in sync.
- **Async end-to-end.** asyncpg + SQLAlchemy 2.x async ORM + FastAPI's
  async dependency injection.
- **Decimal money.** Every monetary field uses `Numeric(10, 2)` in the
  DB and Python `Decimal`, serialized as a string in GraphQL — no
  floating-point rounding errors.
- **Soft delete for services.** Deactivating a service preserves its
  history through past appointments while removing it from the active
  catalog.

---

## Stack

| Layer       | Choice                          |
|-------------|---------------------------------|
| Language    | Python 3.11+                    |
| Web         | FastAPI                         |
| GraphQL     | Strawberry GraphQL              |
| ORM         | SQLAlchemy 2.x (async)          |
| DB driver   | asyncpg                         |
| Database    | PostgreSQL (Supabase)           |
| Migrations  | Alembic (async env)             |
| Server      | Uvicorn                         |
| Config      | pydantic-settings               |

---

## Project layout

```
app/
├── main.py                FastAPI app, CORS, /graphql, /health
├── config.py              Pydantic settings loaded from .env
├── database.py            Async engine + request-scoped session dependency
├── models/                SQLAlchemy ORM models
│   ├── client.py
│   ├── staff.py
│   ├── service.py
│   ├── appointment.py
│   ├── invoice.py
│   ├── payment.py
│   ├── enums.py
│   └── base.py
├── repositories/          Pure DB access per aggregate
├── services/              Business logic (conflict checks, billing rules)
├── graphql/
│   ├── scalars.py         Decimal scalar
│   ├── context.py         FastAPI -> Strawberry context bridge (+ db_lock)
│   ├── extensions.py      SerializeDatabaseAccess extension
│   ├── schema.py          Root schema
│   ├── types/             @strawberry.type output definitions
│   ├── inputs/            @strawberry.input mutation inputs
│   ├── queries/           Query resolvers (one mixin per domain)
│   └── mutations/         Mutation resolvers (one mixin per domain)
└── migrations/            Alembic migration scripts
schema.sql                 Standalone Postgres DDL (Supabase SQL editor)
alembic.ini
requirements.txt
.env.example
```

---

## Setup

### 1. Install dependencies

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and set `DATABASE_URL`. **Use the asyncpg
driver and URL-encode the password.**

```env
DATABASE_URL=postgresql+asyncpg://postgres:URL_ENCODED_PASSWORD@db.YOUR_REF.supabase.co:5432/postgres
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000"]
```

| Connection | Port | Use when                                    |
|------------|------|---------------------------------------------|
| Direct     | 5432 | Local development, IPv6-capable network     |
| PgBouncer  | 6543 | Production (set `DATABASE_POOL_SIZE=1`)     |

### 3. Create the schema

**Easiest:** open the Supabase SQL editor and paste the contents of
`schema.sql`. It creates all tables, enums, indexes, FKs, and triggers
in one shot, idempotently.

**Or with Alembic:**

```powershell
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

### 4. Run

```powershell
uvicorn app.main:app --reload
```

- GraphiQL: <http://localhost:8000/graphql>
- Health:   <http://localhost:8000/health>
- OpenAPI:  <http://localhost:8000/docs>

---

## A complete example flow

```graphql
# 1. Create a service
mutation {
  createService(input: {
    name: "Haircut",
    durationMinutes: 60,
    price: "45.00"
  }) { id }
}

# 2. Create a staff member
mutation {
  createStaff(input: {
    name: "Alex Rivera",
    email: "alex@servicehub.test",
    role: "Senior Stylist",
    specializations: ["color", "cuts"]
  }) { id }
}

# 3. Create a client
mutation {
  createClient(input: {
    name: "Jane Doe",
    email: "jane@example.com"
  }) { id }
}

# 4. Book an appointment
mutation {
  createAppointment(input: {
    clientId:  "…",
    staffId:   "…",
    serviceId: "…",
    scheduledAt: "2026-05-01T14:00:00Z"
  }) {
    id
    status
    service { name price }
  }
}

# 5. Complete the appointment — invoice is auto-generated
mutation {
  completeAppointment(id: "…") {
    status
    invoice { id amount status }
  }
}

# 6. Record a payment — invoice auto-transitions to PAID when total met
mutation {
  recordPayment(input: {
    invoiceId: "…",
    amount: "45.00",
    method: CARD
  }) { id amount }
}

# 7. Inspect everything in one nested query
query {
  appointments(status: COMPLETED) {
    scheduledAt
    client      { name email }
    staffMember { name role }
    service     { name price }
    invoice {
      status
      amount
      amountPaid
      payments { amount method paidAt }
    }
  }
}
```

---

## Documentation

- **`README.md`** — this file (overview + quick start)
- **`dev_guide.md`** — full architectural deep-dive: every layer, every
  design decision, every gotcha
- **`schema.sql`** — standalone DDL for the Supabase SQL editor

---

## License

Internal project — license to be determined.
