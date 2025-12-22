{{ config(materialized='view') }}

with invoice_lines as (
    select
        invoice_line_id,
        invoice_id,
        subscription_id,
        customer_id,
        plan_id,
        line_type,
        amount,
        quantity,
        description,
        service_period_start,
        service_period_end,
        is_recurring,
        is_proration,
        is_adjustment,
        is_credit
    from {{ ref('stg_invoice_lines') }}
),
invoices as (
    select
        invoice_id,
        subscription_id,
        customer_id,
        invoice_status,
        currency,
        total_amount,
        issued_at,
        paid_at,
        invoice_period_start,
        invoice_period_end,
        is_paid,
        is_uncollectible,
        days_to_payment
    from {{ ref('stg_invoices') }}
),
plans as (
    select
        plan_id,
        plan_name,
        billing_frequency,
        billing_period_months
    from {{ ref('stg_plans') }}
),
enriched as (
    select
        invoice_lines.invoice_line_id,
        invoice_lines.invoice_id,
        invoice_lines.subscription_id,
        invoice_lines.customer_id,
        invoice_lines.plan_id,
        
        -- Invoice context
        invoices.invoice_status,
        invoices.currency,
        invoices.total_amount as invoice_total_amount,
        invoices.issued_at,
        invoices.paid_at,
        invoices.is_paid as is_paid_invoice,
        invoices.is_uncollectible,
        invoices.days_to_payment,
        
        -- Plan context
        plans.plan_name,
        plans.billing_frequency,
        plans.billing_period_months,
        
        -- Line details
        invoice_lines.line_type,
        invoice_lines.amount,
        invoice_lines.quantity,
        invoice_lines.description,
        invoice_lines.service_period_start,
        invoice_lines.service_period_end,
        
        -- Derived flags
        invoice_lines.is_recurring,
        invoice_lines.is_proration,
        invoice_lines.is_adjustment,
        invoice_lines.is_credit,
        
        -- Additional derived fields
        case
            when invoice_lines.line_type = 'proration_credit' then true
            else false
        end as is_proration_credit,
        
        case
            when invoice_lines.line_type = 'proration_charge' then true
            else false
        end as is_proration_charge,
        
        -- Service days calculation
        case
            when invoice_lines.service_period_start is not null 
                and invoice_lines.service_period_end is not null
            then invoice_lines.service_period_end - invoice_lines.service_period_start
            else null
        end as service_days,
        
        -- Net amount (consistent naming)
        invoice_lines.amount as net_amount
        
    from invoice_lines
    left join invoices
        on invoice_lines.invoice_id = invoices.invoice_id
    left join plans
        on invoice_lines.plan_id = plans.plan_id
)

select
    invoice_line_id,
    invoice_id,
    subscription_id,
    customer_id,
    plan_id,
    invoice_status,
    currency,
    invoice_total_amount,
    issued_at,
    paid_at,
    is_paid_invoice,
    is_uncollectible,
    days_to_payment,
    plan_name,
    billing_frequency,
    billing_period_months,
    line_type,
    amount,
    net_amount,
    quantity,
    description,
    service_period_start,
    service_period_end,
    service_days,
    is_recurring,
    is_proration,
    is_proration_credit,
    is_proration_charge,
    is_adjustment,
    is_credit
from enriched
