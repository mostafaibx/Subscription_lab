# Subscription Analytics - dbt Project

A complete dbt project that transforms raw subscription billing data into analytics-ready models for MRR tracking, churn analysis, and customer lifecycle metrics.

This project demonstrates subscription analytics patterns I studied and implemented to deepen my understanding of MRR modeling, temporal data, and dbt best practices.

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
│       └── core/                 # Dimensional model (dims + facts)
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

This project uses **deterministic edge cases** (S001-S018) with known expected values.

### Test Layers

| Layer | Type | Purpose |
|-------|------|---------|
| **Schema Tests** | YAML-based | PK/FK integrity, enum validation, `mrr >= 0` |
| **Edge Case Tests** | SQL singular | Prove specific business scenarios work correctly |

### What the Tests Prove

| Test | Scenario | Business Rule |
|------|----------|---------------|
| `test_s001_monthly_mrr_correctness` | Happy path | Monthly MRR = plan price |
| `test_s002_annual_mrr_normalization` | Annual plan | MRR = annual price ÷ 12 |
| `test_s003_cancel_stops_mrr` | Churn | MRR = 0 after cancel date |
| `test_s005_proration_pairing` | Upgrade | Proration credit + charge exist |
| `test_s009_downgrade_at_renewal` | Downgrade | No mid-cycle MRR change |
| `test_s011_pause_mrr_zero` | Pause/resume | MRR = 0 during pause window |
| `test_s013_cancel_reactivate` | Reactivation | MRR returns after reactivate |
| `test_s014_delinquent_mrr_zero` | Payment failure | MRR = 0 during delinquent window |
| `test_invoices_total_reconcile` | Billing audit | Invoice total = sum(lines) |

### Running Tests

```bash
dbt test                              # Run all 200+ tests
dbt test --select test_type:singular  # Run edge case tests only
dbt test --select fct_mrr_daily       # Test a specific model
```

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

---

## Concepts Used

A summary of concepts applied across this project. See each layer's README for detailed explanations.

**dbt & Data Engineering**
- Layered architecture (staging → intermediate → marts)
- `source()` and `ref()` for lineage tracking
- YAML-based testing and documentation
- Materialization strategy (views vs tables)

**Data Modeling**
- Dimensional modeling (star schema)
- Grain definition and enforcement
- SCD Type 2 concepts (status intervals, event-driven tracking)
- Temporal modeling with date spines

**Subscription Analytics**
- MRR calculation and daily snapshots
- Movement classification (new/churn/expansion/contraction)
- Customer cohort assignment
- NRR (Net Revenue Retention) foundations

**Testing & Quality**
- Deterministic test data with known expected values (S001-S018)
- Schema tests: PK/FK integrity, enum validation, expression rules
- Singular tests: Edge case assertions for billing logic
- 200+ automated tests covering MRR, proration, state transitions
