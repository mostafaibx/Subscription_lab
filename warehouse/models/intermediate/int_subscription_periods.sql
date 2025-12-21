{{ config(materialized='view') }}

{# 
For active subscriptions without a cancel date, we need a "current active until" date.
Using current_period_end for active subscriptions gives us the most accurate picture.
If that is null, we use current_date as a conservative estimate.
#}

with base as (
    select
        subscription_id,
        customer_id,
        plan_id,
        status,
        auto_renew,
        date_trunc('day', started_at)::date as start_date,
        cast(canceled_at as date) as cancel_date,
        date_trunc('day', current_period_start)::date as current_period_start,
        date_trunc('day', current_period_end)::date as current_period_end
    from {{ ref('stg_subscriptions') }}
),
normalized as (
    select
        *,
        start_date as active_from_date,
        case
            -- If canceled, use the cancel date
            when cancel_date is not null then cancel_date
            -- For active subscriptions, use current_period_end if available
            when current_period_end is not null then current_period_end
            -- Otherwise use current_date as conservative estimate
            else current_date
        end as active_to_date
    from base
)

select
    subscription_id,
    customer_id,
    plan_id,
    status,
    auto_renew,
    start_date,
    cancel_date,
    active_from_date,
    active_to_date,
    current_period_start,
    current_period_end
from normalized
where start_date is not null