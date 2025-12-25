# Subscription Metrics Lab

An end-to-end **subscription analytics project** that transforms raw billing events into SaaS KPIs (MRR, churn, NRR, cohorts) using **dbt + DuckDB** and delivers insights via **Power BI**.

Built to demonstrate data modeling, analytics engineering, and BI delivery skills.

---

## The Business Problem

Subscription businesses rely on metrics like **MRR, churn, and NRR**—but these are easy to calculate incorrectly when reality includes:
- **monthly vs annual** billing terms
- **mid-cycle upgrades** (proration)
- cancellations, reactivations, pauses
- invoice adjustments (credits/charges)

This project solves that by:
- modeling subscription data with a **grain-first design**
- producing **auditable, tested, and documented** fact tables
- delivering a **Power BI semantic model + measures** suitable for stakeholder analysis

**This project solves that** by building a warehouse that handles these edge cases correctly, with tests that prove it works.

---

## Questions This Project Answers

1. **What is MRR today, and what's driving changes?**
   - New vs churned vs expansion vs contraction MRR

2. **What is our Net Revenue Retention (NRR)?**
   - Are existing customers growing or shrinking over time?

3. **Which customer cohorts retain best/worst?**
   - Logo retention and revenue retention by signup month

4. **How do annual plans and upgrades impact metrics?**
   - MRR normalization and proration tracking

---

## How I Solved It

### 1. Data Generation → Deterministic Test Cases
Built a synthetic data generator with **18 edge cases** (S001-S018) covering:
- Monthly/annual plans, upgrades, downgrades
- Pause/resume, cancel/reactivate
- Payment failures, prorated billing

→ [Data Generation README](data_generation/README.md)

### 2. dbt Warehouse → Layered Transformation
Transformed raw events into a **Kimball star schema** using dbt:

| Layer | Purpose |
|-------|---------|
| **Staging** | Clean, cast, rename raw data |
| **Intermediate** | Business logic: status tracking, MRR calculation, proration |
| **Marts** | Star schema: `dim_customer`, `dim_plan`, `fct_mrr_daily`, etc. |

→ [Warehouse README](warehouse/README.md)

### 3. Testing → Prove the Edge Cases Work
**200+ automated tests** including:
- Schema tests (PK/FK integrity, enum validation)
- Edge case assertions (MRR = 0 when paused, proration pairing, etc.)

### 4. Power BI → Semantic Layer + Dashboard
Built a semantic model on the star schema with DAX measures for:
- MRR trends and MRR bridge (new/churn/expansion/contraction)
- NRR calculation
- Cohort retention heatmaps

---

## Key Modeling Decisions

| Decision | Rationale |
|----------|-----------|
| **Contract-based MRR** | MRR derived from subscription status + plan, not invoice amounts |
| **Daily snapshot fact** | `fct_mrr_daily` enables point-in-time MRR queries without complex windowing |
| **Proration via invoice lines** | Credits/charges are explicit line items for full auditability |
| **Annual normalization** | `mrr = price / billing_period_months` makes monthly + annual comparable |
| **Downgrade at renewal** | Keeps v1 simple—no mid-cycle downgrade proration |

---

## Stack

| Component | Technology |
|-----------|------------|
| **Warehouse** | DuckDB (local), portable to Snowflake/BigQuery |
| **Transform** | dbt-core with dbt-utils |
| **Data Generation** | Python (pandas, numpy, Faker) |
| **Dashboard** | Power BI |

---

## Quick Start

```bash
# 1. Generate synthetic data
cd data_generation
pip install -r requirements.txt
python generate.py

# 2. Load into DuckDB and run dbt
cd ../warehouse
pip install dbt-core dbt-duckdb
python ../scripts/load_duckdb_raw.py
dbt deps
dbt build   # runs models + 200+ tests
```

---

## Project Structure

```
Subscription_lab/
├── README.md                    # ← You are here
├── data_generation/             # Synthetic data generator
│   ├── generate.py              # Entry point
│   ├── edge_cases.py            # S001-S018 deterministic scenarios
│   ├── random_data.py           # Probability-based bulk data
│   └── README.md                # Generator documentation
├── warehouse/                   # dbt project
│   ├── models/
│   │   ├── staging/             # Clean raw data
│   │   ├── intermediate/        # Business logic
│   │   └── marts/core/          # Star schema
│   ├── tests/                   # Edge case assertions
│   └── README.md                # Warehouse documentation
└── scripts/
    └── load_duckdb_raw.py       # Load CSVs into DuckDB
```

---

## What I Learned

Building this project deepened my understanding of:

- **MRR modeling** — why contract-based MRR differs from invoice-based, and when each matters
- **Temporal data** — using date spines and daily snapshots for accurate time-series
- **Event sourcing** — how lifecycle events enable state reconstruction
- **Testing strategy** — deterministic edge cases as a "golden dataset" for validation
- **dbt patterns** — layered architecture, incremental thinking, documentation-as-code

---

## Scope & Limitations

### What's Included (v1)
- Monthly + annual plans (single currency)
- Upgrade proration (mid-cycle)
- Core lifecycle: create, cancel, pause, resume, reactivate
- Payment failure → delinquent → recovery
- MRR, churn, NRR, cohort metrics

### Intentionally Excluded
- Multi-currency / FX
- Complex proration (downgrades, refunds, taxes)
- Usage-based billing, add-ons, bundles

> The goal is to demonstrate correct modeling without overengineering.

---

## Further Reading

| Document | What It Covers |
|----------|----------------|
| [Data Generation README](data_generation/README.md) | How synthetic data is generated, edge case catalog |
| [Warehouse README](warehouse/README.md) | dbt project structure, models, testing strategy |
