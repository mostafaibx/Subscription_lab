{{ config(materialized='table') }}

with source as (
    select
        invoice_line_id,
        invoice_id,
        subscription_id,
        customer_id,
        plan_id,
        issued_at,
        paid_at,
        invoice_status,
        line_type,
        amount,
        service_period_start,
        service_period_end,
        is_paid_invoice,
        is_proration
    from {{ ref('int_invoice_lines_enriched') }}
),

final as (
    select
        invoice_line_id,
        invoice_id,
        subscription_id,
        customer_id,
        plan_id,
        issued_at,
        paid_at,
        invoice_status,
        line_type,
        amount,
        service_period_start,
        service_period_end,
        is_paid_invoice,
        is_proration
    from source
)

select * from final
