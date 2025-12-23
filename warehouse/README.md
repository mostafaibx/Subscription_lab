# Subscription Analytics - dbt Project

A complete dbt project that transforms raw subscription billing data into analytics-ready models for MRR tracking, churn analysis, and customer lifecycle metrics.

## Quick Start

```bash
# Install dependencies
pip install dbt-core dbt-duckdb
dbt deps

# Load raw data (from repo root)
python scripts/load_duckdb_raw.py

# Run the pipeline
dbt run
dbt test
```

## Project Structure

```
warehouse/
├── models/
│   ├── staging/subscriptions/    # Clean & type raw data
│   ├── intermediate/             # Business logic & daily snapshots
│   └── marts/
│       ├── core/                 # Dimensional model (dims + facts)
│       └── metrics/              # KPI aggregations
├── macros/                       # Reusable SQL functions
├── tests/                        # Custom data tests
└── snapshots/                    # SCD Type 2 tracking
```

## Layer Architecture

| Layer | Purpose | Models | Details |
|-------|---------|--------|---------|
| **Staging** | Clean, cast, rename raw data | 6 models | [→ README](models/staging/subscriptions/README.md) |
| **Intermediate** | Business logic, daily snapshots, MRR calculations | 12 models | [→ README](models/intermediate/README.md) |
| **Marts** | Dimensional model for analytics | 7 models | dims + facts |


## Key Models

### Staging (6 models)
Cleans raw data with consistent typing, naming conventions, and pre-computed boolean flags.

### Intermediate (12 models)

| Model | Purpose |
|-------|---------|
| `int_date_spine` | Calendar spine for daily snapshots |
| `int_subscription_periods` | Normalized subscription coverage windows |
| `int_subscription_status_*` | Status tracking (segments → daily) |
| `int_plan_daily` | Daily plan assignments |
| `int_mrr_contract_daily` | Daily MRR per subscription |
| `int_customer_mrr_daily` | Daily MRR per customer |
| `int_nrr_base_monthly` | Monthly MRR snapshots for NRR |
| `int_mrr_movements` | MRR movement classification (new/churn/expansion/contraction) |

### Marts (7 models)

| Model | Type | Purpose |
|-------|------|---------|
| `dim_customer` | Dimension | Customer attributes + cohort |
| `dim_plan` | Dimension | Plan definitions |
| `dim_subscription` | Dimension | Subscription details |
| `dim_date` | Dimension | Date attributes |
| `fct_mrr_daily` | Fact | Daily MRR snapshots |
| `fct_invoice_lines` | Fact | Invoice line items |
| `fct_subscription_events` | Fact | Subscription lifecycle events |

## Testing

```bash
dbt test                              # Run all tests
dbt test --select staging             # Test staging only
dbt test --select tag:primary_key     # Test PKs only
```

Test coverage includes:
- Primary key integrity (`unique` + `not_null`)
- Foreign key relationships
- Enum value validation
- Business rule assertions

## Commands Reference

```bash
dbt run                               # Build all models
dbt run --select staging              # Build staging only
dbt run --select +fct_mrr_daily       # Build fct_mrr_daily and all upstream
dbt docs generate && dbt docs serve   # View documentation
```

## Configuration

- **Profile**: Copy `profiles.yml` to `~/.dbt/profiles.yml`
- **Database**: DuckDB (local), Snowflake, or BigQuery
- **Packages**: `dbt-utils` for date spine and testing utilities
