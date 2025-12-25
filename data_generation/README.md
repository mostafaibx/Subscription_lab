# Subscription Data Generator

Synthetic data generator for SaaS subscription billing — designed to produce realistic test data with known edge cases.

## Why This Exists

Testing subscription metrics (MRR, churn, proration) requires data with **predictable outcomes**. This generator creates:

- **18 deterministic edge cases** (S001–S018) with exact values for unit testing
- **Random bulk data** following configurable probability distributions

## Quick Start

```bash
pip install -r requirements.txt
python generate.py
```

Output lands in `output/` as 6 CSV files ready for warehouse ingestion.

## Project Structure

```
data_generation/
├── generate.py        # Entry point — orchestrates everything
├── edge_cases.py      # S001-S018 deterministic test scenarios
├── random_data.py     # Probability-based bulk generation
├── utils.py           # Shared helpers (IDs, dates, proration math)
├── config.yml         # Plans, probabilities, settings
└── output/            # Generated CSVs
```

## How It Works

### Script Flow

```
generate.py (entry point)
    │
    ├─→ Load config.yml + set random seed
    │
    ├─→ edge_cases.py
    │       └─→ 18 scenario functions (s001...s018)
    │           Each returns: (subscription, events, invoices, lines)
    │
    ├─→ random_data.py
    │       └─→ Generate customers → subscriptions → events/invoices
    │           Uses probability rolls for edge cases (cancel, upgrade, pause...)
    │
    ├─→ Combine edge cases + random data
    │
    └─→ Write 6 CSV files to output/
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `generate.py` | Orchestration only — no business logic |
| `edge_cases.py` | Hardcoded test scenarios with exact expected values |
| `random_data.py` | Probability-driven generation using config settings |
| `utils.py` | Pure helper functions — reusable across modules |

### Data Generation Pattern

Each subscription generates a **consistent set of related records**:

```python
# 1. Subscription record (current state snapshot)
subscription = {subscription_id, customer_id, plan_id, status, ...}

# 2. Event log (immutable history — enables state reconstruction)
events = [
    {event_type: 'created', occurred_at: ...},
    {event_type: 'plan_changed', old_plan_id: ..., new_plan_id: ...},
    {event_type: 'canceled', ...}
]

# 3. Invoice + lines (billing audit trail)
invoice = {invoice_id, issued_at, paid_at, total_amount, ...}
lines = [
    {line_type: 'recurring_charge', amount: 30},
    {line_type: 'proration_credit', amount: -20},  # upgrade credit
    {line_type: 'proration_charge', amount: 40}    # upgrade charge
]
```

## Design Decisions

| Decision | Reasons |
|----------|-----------|
| **Configuration-driven** | All probabilities/settings in `config.yml` — no magic numbers |
| **Seeded randomness** | `np.random.seed(42)` → identical output every run (CI-friendly) |
| **ID namespacing** | Edge cases use IDs 1-99, random data uses 100+ (no collisions) |
| **Event sourcing** | Events table enables state reconstruction & SCD Type 2 in dbt |
| **UTC timestamps** | Prevents timezone bugs in billing calculations |
| **30/360 day convention** | Industry-standard simplification for proration math |
| **Centralized proration** | Single formula in `utils.py` used by all modules |

## Output Schema

| File | Purpose |
|------|---------|
| `raw_customers.csv` | Customer master data |
| `raw_plans.csv` | Plan catalog (Basic/Pro × Monthly/Annual) |
| `raw_subscriptions.csv` | Current subscription state |
| `raw_subscription_events.csv` | Lifecycle events (created, upgraded, cancelled...) |
| `raw_invoices.csv` | Invoice headers with `issued_at` and `paid_at` |
| `raw_invoice_lines.csv` | Line items including proration credits/charges |

### Sample Output (invoice_lines)

```
invoice_line_id | line_type         | amount  | plan_id
----------------|-------------------|---------|------------
LINE_00001      | recurring_charge  |  30.00  | P_BASIC_M_30
LINE_00002      | proration_credit  | -20.00  | P_BASIC_M_30
LINE_00003      | proration_charge  |  40.00  | P_PRO_M_60
```

## Edge Cases (S001–S018)

18 deterministic scenarios covering key billing behaviors:

| Category | Scenarios | What It Tests |
|----------|-----------|---------------|
| Happy path | S001–S002 | Monthly & annual MRR calculation |
| Churn | S003–S004 | Early vs long-tenure cancellation |
| Upgrades | S005–S008 | Proration math, double upgrades |
| Downgrades | S009–S010 | Effective at next renewal |
| Pause/Cancel | S011–S013 | State transitions, reactivation |
| Edge cases | S014–S018 | Payment failure, adjustments, boundary dates |

## Configuration

All settings live in `config.yml`:

```yaml
seed: 42                    # Reproducibility

sizes:
  random_customers: 300
  random_subscriptions: 450

randomization:
  prob_cancel: 0.10         # 10% cancel
  prob_upgrade: 0.08        # 8% upgrade with proration
  prob_pause: 0.06
  prob_delinquent: 0.04
```

## Extending

**Add a new edge case:**
1. Create `s019_your_scenario()` in `edge_cases.py`
2. Add it to the `scenarios` list in `generate_all_edge_cases()`

**Add a new event type:**
1. Add probability to `config.yml`
2. Add logic branch in `random_data.py`

## Tech Stack

- Python 3.10+
- pandas (data manipulation)
- numpy (random generation)
- Faker (realistic names/emails)
- PyYAML (config loading)

## Documentation

- **[`docs/architecture.md`](../docs/architecture.md)** — Full schema definitions, data contracts, and entity relationships
