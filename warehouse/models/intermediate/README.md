# Intermediate Models

This layer contains business logic transformations — joins across entities, temporal expansions, and metric calculations that bridge staging to marts.

## Models

Organized by functional area:

### Date Infrastructure

| Model | Purpose |
|-------|---------|
| `int_date_spine` | Continuous calendar spine for daily snapshots |

### Subscription Status Pipeline

| Model | Purpose |
|-------|---------|
| `int_subscription_periods` | Normalized coverage windows per subscription |
| `int_subscription_status_segments` | Non-overlapping status intervals from lifecycle events |
| `int_subscription_status_daily` | Daily status snapshot per subscription |

### Plan Assignment Pipeline

| Model | Purpose |
|-------|---------|
| `int_plan_events_timeline` | Non-overlapping plan intervals from events |
| `int_plan_daily` | Daily plan assignment per subscription |

### MRR Calculation Pipeline

| Model | Purpose |
|-------|---------|
| `int_mrr_contract_daily` | Daily MRR per subscription (status × plan × price) |
| `int_customer_mrr_daily` | Daily MRR aggregated to customer level |
| `int_nrr_base_monthly` | Monthly MRR snapshots for NRR calculation |
| `int_mrr_movements` | MRR movement classification (new/churn/expansion/contraction) |

### Supporting Models

| Model | Purpose |
|-------|---------|
| `int_first_paid_date` | First paid invoice per customer for cohort assignment |
| `int_invoice_lines_enriched` | Invoice lines with payment and plan context |

## Naming Conventions

- **int_** prefix for all intermediate models
- **_daily** suffix for day-grain snapshot tables
- **_monthly** suffix for month-grain aggregations
- **_segments** / **_timeline** suffix for interval-based models

## Data Quality Tests

Tests are defined in `_schema.yml`. The testing strategy validates grain, business rules, and data integrity.

### Test Coverage

| Test Type | Purpose | Applied To |
|-----------|---------|------------|
| `unique` + `not_null` | Single-column PK integrity | `int_date_spine`, `int_subscription_periods`, `int_invoice_lines_enriched`, `int_first_paid_date` |
| `unique_combination_of_columns` | Composite key integrity | All daily/monthly grain tables |
| `accepted_values` | Enum validation | `status`, `daily_status`, `movement_type`, `line_type` |
| `expression_is_true` | Business rule validation | `mrr >= 0` checks |
| `not_null` | Required field validation | Core identifiers and metrics |

### Grain Enforcement

Each daily model enforces one row per entity per day:

```
int_subscription_status_daily  →  (subscription_id, date_day)
int_plan_daily                 →  (subscription_id, date_day)
int_mrr_contract_daily         →  (subscription_id, date_day)
int_customer_mrr_daily         →  (customer_id, date_day)
int_nrr_base_monthly           →  (customer_id, month)
int_mrr_movements              →  (customer_id, month)
```

### Enum Validations

| Column | Valid Values |
|--------|--------------|
| `status` / `daily_status` | active, paused, canceled, delinquent |
| `movement_type` | new, churn, expansion, contraction, retained, no_mrr |
| `change_type` | created, plan_changed |
| `line_type` | recurring_charge, proration_credit, proration_charge, adjustment |

### Running Tests

```bash
# Run all intermediate tests
dbt test --select intermediate

# Run tests for a specific model
dbt test --select int_mrr_contract_daily
```

## Design Decisions

Key modeling patterns applied in this intermediate layer:

### Date Spine Pattern

**Simpler alternative:** Query events directly with `DATE_TRUNC('day', occurred_at)` and aggregate. This approach will work in our use case but it might create gaps in bigger projects e.g. days with no events have no rows.

| Aspect | Implementation |
|--------|----------------|
| Purpose | Provides a continuous calendar for temporal joins |
| Range | Driven by data or configurable overrides |
| Grain | One row per calendar day |
| Use | Cross-join source for daily snapshot expansion |

### Interval-to-Daily Expansion

Status and plan changes arrive as events. We expand them to daily snapshots:

```
Events:  [created: Jan 1] → [paused: Jan 15] → [resumed: Jan 20]
                ↓
Segments: Jan 1-14: active | Jan 15-19: paused | Jan 20+: active
                ↓
Daily:    Jan 1: active, Jan 2: active, ..., Jan 15: paused, ...
```

This pattern enables:
- Point-in-time queries ("What was MRR on March 15?")
- Period aggregations ("Total active days in Q1")
- Trend analysis without complex window functions

### Hybrid Event-Snapshot Pattern

we have other simplier alternatives e.g. (1) Use only the subscription table's current `status` column or (2) Derive status purely from events.
In our usecase with the generated dataset simple approach would be enough, however I chose this pattern to study it would fit production datasets.

`int_subscription_status_segments` merges two data sources:

| Source | Priority | Purpose |
|--------|----------|---------|
| Event log | 0 (higher) | Detailed history of status changes |
| Subscription table | 1 (lower) | Current state as fallback |

Uses `row_number()` with priority ordering to deduplicate same-day records.

### MRR Policy Implementation

| Status | MRR Policy |
|--------|------------|
| `active` | Plan's MRR value |
| `paused` | 0 (not billing) |
| `canceled` | 0 (churned) |
| `delinquent` | 0 (payment failed) |

This policy is centralized in `int_mrr_contract_daily` — downstream models inherit it.

### Movement Classification Logic

`int_mrr_movements` classifies customer MRR changes:

| Condition | Movement Type |
|-----------|---------------|
| `mrr_start = 0 AND mrr_end > 0` | new |
| `mrr_start > 0 AND mrr_end = 0` | churn |
| `mrr_end > mrr_start` | expansion |
| `mrr_end < mrr_start` | contraction |
| `mrr_end = mrr_start` | retained |

This feeds MRR bridge reporting and cohort retention analysis.

### Layer Responsibilities

Intermediate models intentionally:
- ✅ Join across staging entities
- ✅ Expand intervals to daily grain
- ✅ Calculate intermediate metrics (MRR per subscription)
- ✅ Classify events and movements

Intermediate models avoid:
- ❌ Final aggregations for reporting (belongs in marts)
- ❌ Denormalized wide tables (belongs in dims/facts)
- ❌ End-user facing column names (marts handle presentation)

---

## Used Concepts

A quick summary of concepts applied in this intermediate layer:

**Temporal Modeling**
- Date spine generation for continuous time series
- Interval-to-daily expansion pattern
- Point-in-time correctness for historical queries

**SCD Type 2 Techniques**
- Event-driven status tracking
- Non-overlapping interval construction with `LEAD()` window function
- Priority-based deduplication for hybrid sources

**MRR Analytics**
- Contract-based MRR calculation
- Customer-level aggregation
- Monthly snapshot conversion for NRR
- Movement classification (new/churn/expansion/contraction)

**Testing Patterns**
- Composite key uniqueness with `dbt_utils`
- Business rule validation with `expression_is_true`
- Grain enforcement at each pipeline stage

**Code Quality**
- Consistent naming (`int_`, `_daily`, `_monthly`)
- CTE-based structure for readability
- Centralized business logic (MRR policy in one place)
- Clear model dependencies for DAG clarity
