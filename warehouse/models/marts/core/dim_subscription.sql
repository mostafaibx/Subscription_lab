{{ config(materialized='table') }}

with subscription_periods as (
    select
        subscription_id,
        customer_id,
        plan_id,
        status,
        auto_renew,
        start_date,
        cancel_date,
        current_period_start,
        current_period_end
    from {{ ref('int_subscription_periods') }}
),

final as (
    select
        subscription_id,
        customer_id,
        start_date,
        cancel_date,
        auto_renew,
        plan_id as current_plan_id,
        current_period_start,
        current_period_end,
        status as current_status
    from subscription_periods
)

select * from final
