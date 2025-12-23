{{ config(materialized='table') }}

with source as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        daily_status,
        mrr
    from {{ ref('int_mrr_contract_daily') }}
),

final as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        daily_status,
        mrr
    from source
)

select * from final
