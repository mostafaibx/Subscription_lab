# Intermediate Models

This layer contains business logic transformations.


## Models

| Model | Purpose | Feeds Into |
|-------|---------|------------|
| `int_date_spine` | Continuous calendar spine used by daily snapshots; range can be driven by data or overrides | `int_subscription_status_daily`, `fct_mrr_daily` |
| `int_subscription_periods` | Canonical coverage window per subscription; normalizes active bounds against configured end dates | `int_subscription_status_daily`, `fct_mrr_daily` |
| `int_subscription_status_segments` | Non-overlapping historical and current status intervals derived from lifecycle events; enforces pause/delinquency policies for downstream MRR | `int_subscription_status_daily`, `fct_mrr_daily` |
| `int_subscription_status_daily` | Expands status intervals to daily rows within coverage windows; provides one snapshot per subscription per day | `fct_mrr_daily` |
| `int_plan_events_timeline` | Non-overlapping plan intervals showing which plan is active on which dates; merges creation and plan_changed events | `int_plan_daily`, `fct_mrr_daily` |
| `int_plan_daily` | Expands plan intervals to daily rows; assigns the effective plan_id per subscription per day for MRR lookup | `int_mrr_contract_daily` |
| `int_mrr_contract_daily` | Computes daily contract-based MRR by joining status, plan, and pricing; applies v1 policy (active=plan MRR, else 0) | `int_customer_mrr_daily`, `fct_mrr_daily` |
| `int_invoice_lines_enriched` | Enriches invoice lines with invoice status, payment info, and plan context for proration audits and billing analysis | Billing reports, proration audits |
| `int_first_paid_date` | Identifies first paid invoice date per customer for cohort assignment and activation tracking | `int_customer_cohorts`, `dim_customer` |
| `int_customer_mrr_daily` | Aggregates subscription MRR to customer level per day for NRR and customer-level KPI analysis | `int_nrr_base_monthly`, NRR metrics |
| `int_nrr_base_monthly` | Converts daily customer MRR to monthly start/end snapshots for NRR calculation at portfolio level | NRR metrics, retention analysis |
| `int_mrr_movements` | Classifies monthly MRR movement per customer (new/churn/expansion/contraction/retained) by comparing month start vs end | MRR bridge metrics |
