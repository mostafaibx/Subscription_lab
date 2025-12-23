# Staging Models: Subscriptions

This folder contains the staging layer that clean, rename, cast and add dreived flags.

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