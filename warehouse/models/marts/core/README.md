# Marts: Core

This layer contains the final dimensional model — dimensions and facts ready for BI tools and reporting.

## Models

### Dimensions

| Model | Grain | Description |
|-------|-------|-------------|
| `dim_date` | One row per day | Calendar attributes for date joins |
| `dim_customer` | One row per customer | Customer attributes + first paid date |
| `dim_plan` | One row per plan | Plan details and pricing |
| `dim_subscription` | One row per subscription | Current subscription state |

### Facts

| Model | Grain | Description |
|-------|-------|-------------|
| `fct_mrr_daily` | One row per subscription per day | Daily MRR snapshots |
| `fct_subscription_events` | One row per event | Subscription lifecycle events |
| `fct_invoice_lines` | One row per line item | Invoice details for billing analysis |

## Naming Conventions

- **dim_** prefix for dimension tables
- **fct_** prefix for fact tables
- Materialized as `table` for query performance

## Data Quality Tests

Tests are defined in `_core.yml`.

### Test Coverage

| Test Type | Purpose | Applied To |
|-----------|---------|------------|
| `unique` + `not_null` | Primary key integrity | All dimension PKs, `fct_subscription_events`, `fct_invoice_lines` |
| `unique_combination_of_columns` | Composite key integrity | `fct_mrr_daily` (subscription × date) |
| `relationships` | Foreign key validation | Fact → Dimension joins |
| `accepted_values` | Enum validation | Status and type columns |
| `expression_is_true` | Business rules | `mrr >= 0`, proration sign checks |

### Relationships

```
fct_mrr_daily.date_day         →  dim_date.date_day
fct_mrr_daily.subscription_id  →  dim_subscription.subscription_id
fct_mrr_daily.plan_id          →  dim_plan.plan_id
dim_subscription.customer_id   →  dim_customer.customer_id
dim_subscription.current_plan_id  →  dim_plan.plan_id
```

## Design Decisions

### Why Dimensional Modeling?

Simpler alternatives exist — like flat tables with all columns denormalized. Dimensional modeling (star schema) is the standard for analytics because:
- **Efficient joins** — Facts reference dimensions by ID
- **Consistent attributes** — Customer name lives in one place
- **BI tool friendly** — Tools like Looker/Tableau expect this structure

### Materialization

| Layer | Materialization | Why |
|-------|-----------------|-----|
| Staging | View | Light transformations, always fresh |
| Intermediate | View | Business logic, rebuilt on demand |
| **Marts** | **Table** | Query performance for end users |

### Denormalized Fields

Some foreign keys are repeated in facts for convenience:

```sql
-- fct_mrr_daily includes customer_id directly
-- Avoids extra join through dim_subscription for common queries
```

This trades slight redundancy for simpler queries in BI tools.

### Thin Fact Tables

`fct_mrr_daily` is intentionally thin — it pulls from `int_mrr_contract_daily` without adding extra columns. This keeps facts focused on measures and foreign keys. Additional context comes from dimension joins.

---

## Used Concepts

- Star schema with facts and dimensions
- Grain definition for each table
- Table materialization for query performance
- Referential integrity with relationship tests
- Consistent naming (`dim_`, `fct_`)
