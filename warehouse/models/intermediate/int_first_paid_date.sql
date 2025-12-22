{{ config(materialized='view') }}

with paid_invoices as (
    select
        customer_id,
        paid_at,
        invoice_id,
        invoice_status
    from {{ ref('stg_invoices') }}
    where invoice_status = 'paid'
        and paid_at is not null
),
first_paid as (
    select
        customer_id,
        min(paid_at) as first_paid_at
    from paid_invoices
    group by customer_id
),
enriched as (
    select
        customer_id,
        first_paid_at,
        date_trunc('day', first_paid_at)::date as first_paid_date,
        date_trunc('month', first_paid_at)::date as first_paid_month
    from first_paid
)

select
    customer_id,
    first_paid_at,
    first_paid_date,
    first_paid_month
from enriched
order by customer_id;
