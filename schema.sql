-- =====================================================================
-- ServiceHub initial schema
-- Paste into the Supabase SQL editor and run.
-- Safe to re-run: every CREATE uses IF NOT EXISTS where possible.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------
-- `gen_random_uuid()` is provided by pgcrypto (pre-installed on Supabase).
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------
-- Enum types
-- ---------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE appointment_status AS ENUM ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE invoice_status AS ENUM ('PENDING', 'PAID', 'OVERDUE');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE payment_method AS ENUM ('CASH', 'CARD', 'ONLINE');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------
-- Shared trigger function: auto-maintain updated_at on UPDATE
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------
-- clients
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clients (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    email       VARCHAR(320) NOT NULL UNIQUE,
    phone       VARCHAR(50),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_clients_email ON clients(email);

DROP TRIGGER IF EXISTS trg_clients_updated_at ON clients;
CREATE TRIGGER trg_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- staff
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS staff (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(200) NOT NULL,
    email            VARCHAR(320) NOT NULL UNIQUE,
    role             VARCHAR(100) NOT NULL,
    specializations  VARCHAR(100)[] NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_staff_email ON staff(email);

DROP TRIGGER IF EXISTS trg_staff_updated_at ON staff;
CREATE TRIGGER trg_staff_updated_at
    BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- services
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS services (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name              VARCHAR(200) NOT NULL UNIQUE,
    description       TEXT,
    duration_minutes  INTEGER NOT NULL,
    price             NUMERIC(10, 2) NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_services_updated_at ON services;
CREATE TRIGGER trg_services_updated_at
    BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- appointments
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS appointments (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id     UUID NOT NULL REFERENCES clients(id)  ON DELETE CASCADE,
    staff_id      UUID NOT NULL REFERENCES staff(id)    ON DELETE CASCADE,
    service_id    UUID NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    scheduled_at  TIMESTAMPTZ NOT NULL,
    status        appointment_status NOT NULL DEFAULT 'PENDING',
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_staff_scheduled_at UNIQUE (staff_id, scheduled_at)
);
CREATE INDEX IF NOT EXISTS ix_appointments_client_id    ON appointments(client_id);
CREATE INDEX IF NOT EXISTS ix_appointments_staff_id     ON appointments(staff_id);
CREATE INDEX IF NOT EXISTS ix_appointments_service_id   ON appointments(service_id);
CREATE INDEX IF NOT EXISTS ix_appointments_scheduled_at ON appointments(scheduled_at);

DROP TRIGGER IF EXISTS trg_appointments_updated_at ON appointments;
CREATE TRIGGER trg_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- invoices (one-to-one with appointments)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id  UUID NOT NULL UNIQUE REFERENCES appointments(id) ON DELETE CASCADE,
    amount          NUMERIC(10, 2) NOT NULL,
    status          invoice_status NOT NULL DEFAULT 'PENDING',
    issued_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_invoices_updated_at ON invoices;
CREATE TRIGGER trg_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- payments (many per invoice — supports partial / split payments)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id  UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    amount      NUMERIC(10, 2) NOT NULL,
    method      payment_method NOT NULL,
    paid_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_payments_invoice_id ON payments(invoice_id);

DROP TRIGGER IF EXISTS trg_payments_updated_at ON payments;
CREATE TRIGGER trg_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- Enum types for expenses and salaries
-- ---------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE expense_category AS ENUM ('SUPPLIES', 'EQUIPMENT', 'RENT', 'UTILITIES', 'MARKETING', 'TRAVEL', 'TRAINING', 'MAINTENANCE', 'OTHER');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE expense_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'REIMBURSED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE salary_status AS ENUM ('PENDING', 'PAID', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------
-- expenses (business expenses, optionally linked to a staff member)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description   VARCHAR(500) NOT NULL,
    amount        NUMERIC(10, 2) NOT NULL,
    category      expense_category NOT NULL,
    expense_date  DATE NOT NULL,
    status        expense_status NOT NULL DEFAULT 'PENDING',
    staff_id      UUID REFERENCES staff(id) ON DELETE SET NULL,
    receipt_url   VARCHAR(1000),
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_expenses_staff_id     ON expenses(staff_id);
CREATE INDEX IF NOT EXISTS ix_expenses_expense_date ON expenses(expense_date);

DROP TRIGGER IF EXISTS trg_expenses_updated_at ON expenses;
CREATE TRIGGER trg_expenses_updated_at
    BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- salaries (monthly salary disbursements per staff member)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS salaries (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id   UUID NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    amount     NUMERIC(10, 2) NOT NULL,
    pay_year   INTEGER NOT NULL,
    pay_month  INTEGER NOT NULL CHECK (pay_month BETWEEN 1 AND 12),
    status     salary_status NOT NULL DEFAULT 'PENDING',
    paid_at    TIMESTAMPTZ,
    notes      TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_staff_pay_period UNIQUE (staff_id, pay_year, pay_month)
);
CREATE INDEX IF NOT EXISTS ix_salaries_staff_id ON salaries(staff_id);

DROP TRIGGER IF EXISTS trg_salaries_updated_at ON salaries;
CREATE TRIGGER trg_salaries_updated_at
    BEFORE UPDATE ON salaries
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- Column additions — safe to re-run (IF NOT EXISTS guards).
-- =====================================================================

-- Staff: base monthly salary
ALTER TABLE staff ADD COLUMN IF NOT EXISTS monthly_salary NUMERIC(10, 2) NOT NULL DEFAULT 0;

-- Services: GST percentage and bonus/surcharge
ALTER TABLE services ADD COLUMN IF NOT EXISTS gst_percent NUMERIC(5, 2) NOT NULL DEFAULT 0;
ALTER TABLE services ADD COLUMN IF NOT EXISTS bonus NUMERIC(10, 2) NOT NULL DEFAULT 0;

-- Salaries: bonus per disbursement
ALTER TABLE salaries ADD COLUMN IF NOT EXISTS bonus NUMERIC(10, 2) NOT NULL DEFAULT 0;

-- =====================================================================
-- Done. Verify with:
--   SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
-- =====================================================================
