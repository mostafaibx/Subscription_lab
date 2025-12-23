# Staging Models: Subscriptions

This folder contains the staging layer that cleans, renames, casts, and adds derived flags.

## Models

| Model | Source | Description |
|-------|--------|-------------|
| `stg_customers` | `raw_customers` | Customer master data |
| `stg_plans` | `raw_plans` | Plan definitions with billing frequency |
| `stg_subscriptions` | `raw_subscriptions` | Subscriptions with status flags |
| `stg_subscription_events` | `raw_subscription_events` | Lifecycle events |
| `stg_invoices` | `raw_invoices` | Invoice headers with payment flags |
| `stg_invoice_lines` | `raw_invoice_lines` | Line items with type flags |

## Naming Conventions

- **stg_** prefix for all staging models
- **_at** suffix for timestamps (e.g., `created_at`, `canceled_at`)
- **is_** prefix for boolean flags (e.g., `is_canceled`, `is_paid`)
- Snake_case for all column names

## Data Quality Tests

Tests are defined in `_schema.yml` and run via `dbt test`. The testing strategy focuses on essential data integrity without over-engineering.

### Test Coverage

| Test Type | Purpose | Applied To |
|-----------|---------|------------|
| `unique` + `not_null` | Primary key integrity | All `*_id` columns |
| `not_null` | Required field validation | Foreign keys, critical fields |
| `relationships` | Referential integrity | FK → PK mappings |
| `accepted_values` | Enum validation | Status fields, type columns |

### Referential Integrity

```
stg_subscriptions.customer_id  →  stg_customers.customer_id
stg_subscriptions.plan_id      →  stg_plans.plan_id
stg_subscription_events.subscription_id  →  stg_subscriptions.subscription_id
stg_invoices.customer_id       →  stg_customers.customer_id
stg_invoices.subscription_id   →  stg_subscriptions.subscription_id
stg_invoice_lines.invoice_id   →  stg_invoices.invoice_id
```

### Enum Validations

| Column | Valid Values |
|--------|--------------|
| `customer_segment` | SMB, Mid-Market, Enterprise |
| `country` | DE, NL, FR |
| `status` | active, canceled, paused |
| `billing_frequency` | monthly, annual, other |
| `event_type` | created, canceled, paused, resumed, plan_changed, payment_failed, payment_recovered, reactivated |
| `invoice_status` | paid, uncollectible |
| `line_type` | recurring_charge, proration_credit, proration_charge, adjustment |

### Running Tests

```bash
# Run all staging tests
dbt test --select staging.subscriptions

# Run tests for a specific model
dbt test --select stg_customers
```

## Design Decisions

Key modeling patterns applied in this staging layer:

### Structure & Conventions

| Pattern | Implementation | Why It Matters |
|---------|----------------|----------------|
| CTE pattern | `source` → `renamed` → `select` | Standard dbt structure for readability and maintainability |
| `source()` macro | All models reference `{{ source('raw', 'table') }}` | Enables lineage tracking in dbt docs and DAG |
| Column grouping | PK → FK → Attributes → Timestamps → Derived | Consistent organization across all models |
| Explicit type casting | `cast(created_at as timestamp)` | Type safety at the staging layer prevents downstream issues |

### Semantic Renaming

| Original | Renamed To | Reason |
|----------|------------|--------|
| `pause_start_at` | `paused_at` | Matches business language |
| `pause_end_at` | `resumed_at` | Action-oriented naming |
| `status` (invoices) | `invoice_status` | Avoids ambiguity when joining with subscriptions |

### Pre-computed Boolean Flags

Staging creates reusable flags to simplify downstream logic:

| Model | Flag | Logic | Use Case |
|-------|------|-------|----------|
| `stg_subscriptions` | `is_canceled` | `status = 'canceled'` | Churn analysis |
| `stg_subscriptions` | `is_active_recurring` | `status = 'active' AND auto_renew` | Active subscriber counts |
| `stg_subscription_events` | `is_churn_event` | `event_type IN ('canceled', 'churned')` | Churn cohorts |
| `stg_subscription_events` | `is_plan_change` | `event_type = 'plan_changed' AND new_plan_id IS NOT NULL` | Upgrade/downgrade tracking |
| `stg_invoices` | `is_paid` | `status = 'paid'` | Revenue recognition |
| `stg_invoices` | `days_to_payment` | `datediff(issued_at, paid_at)` | Cash flow metrics |
| `stg_invoice_lines` | `is_recurring` | `line_type = 'recurring_charge'` | MRR calculations |
| `stg_invoice_lines` | `is_proration` | Proration credits or charges | Revenue adjustments |
| `stg_invoice_lines` | `is_credit` | `amount < 0` | Credit tracking |

### Layer Separation

Staging models intentionally avoid:
- ❌ Aggregations (belongs in intermediate/marts)
- ❌ Joins across entities (belongs in intermediate)
- ❌ Business KPI calculations (belongs in marts)

This keeps staging focused on **cleaning and typing** — the single responsibility principle applied to data modeling.

---



## Used Concepts

A quick summary of concepts applied in this staging layer:

**dbt Fundamentals**
- CTE-based model structure
- `source()` macro for lineage tracking
- YAML-based schema definitions
- Built-in tests (`unique`, `not_null`, `relationships`, `accepted_values`)

**Data Modeling**
- Staging layer responsibilities (clean, cast, rename — no joins or aggregations)
- Primary key and foreign key identification
- Referential integrity enforcement
- Appropriate data type precision (timestamp vs date)

**Code Quality**
- Consistent naming conventions (`stg_`, `is_`, `_at`)
- Column grouping and organization
- Pre-computed boolean flags for downstream simplicity
- Defensive handling of edge cases

**Best Practices**
- Database-agnostic macros for portability
- Semantic column renaming for business clarity
- Layer separation following the single responsibility principle
- Documentation alongside code