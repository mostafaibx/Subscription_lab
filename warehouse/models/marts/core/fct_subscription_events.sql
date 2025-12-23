{{ config(materialized='table') }}

with source as (
    select
        event_id,
        occurred_at,
        effective_date,
        subscription_id,
        customer_id,
        event_type,
        old_plan_id,
        new_plan_id,
        reason
    from {{ ref('stg_subscription_events') }}
),

final as (
    select
        event_id,
        occurred_at,
        effective_date,
        subscription_id,
        customer_id,
        event_type,
        old_plan_id,
        new_plan_id,
        reason
    from source
)

select * from final
