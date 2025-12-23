{{ config(materialized='table') }}

with source as (
    select
        plan_id,
        plan_name,
        currency,
        billing_period_months,
        price_per_period,
        mrr_equivalent,
        is_active,
        billing_frequency
    from {{ ref('stg_plans') }}
),

final as (
    select
        plan_id,
        plan_name,
        currency,
        billing_period_months,
        price_per_period,
        mrr_equivalent,
        is_active,
        billing_frequency
    from source
)

select * from final
