{{ config(materialized='view') }}

with spine as (
    select date_day
    from {{ ref('int_date_spine') }}
),
periods as (
    select
        subscription_id,
        customer_id,
        plan_id,
        active_from_date,
        active_to_date
    from {{ ref('int_subscription_periods') }}
),
segments as (
    select
        subscription_id,
        status,
        status_start_date,
        status_end_date,
        status_event_id
    from {{ ref('int_subscription_status_segments') }}
),
subscription_days as (
    select
        spine.date_day,
        periods.subscription_id,
        periods.customer_id,
        periods.plan_id
    from spine
    inner join periods
        on spine.date_day >= periods.active_from_date
        and spine.date_day <= periods.active_to_date
),
daily_status as (
    select
        subscription_days.date_day,
        subscription_days.subscription_id,
        subscription_days.customer_id,
        subscription_days.plan_id,
        segments.status as daily_status,
        segments.status_event_id
    from subscription_days
    left join segments
        on subscription_days.subscription_id = segments.subscription_id
        and subscription_days.date_day >= segments.status_start_date
        and (segments.status_end_date is null or subscription_days.date_day < segments.status_end_date)
),

 {# Defensive deduplication: ensures one status per subscription per day
 in case of overlapping segments or data quality issues upstream. we can also use test in schema.yml to ensure this without masking any issues #}


ranked_status as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        coalesce(daily_status, 'active') as daily_status,
        status_event_id,
        row_number() over (
            partition by subscription_id, date_day
            order by status_event_id desc nulls last
        ) as rank_per_day
    from daily_status
),
final as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        daily_status,
        case when daily_status = 'active' then true else false end as is_active_day,
        case when daily_status = 'active' then true else false end as is_billable_day
    from ranked_status
    where rank_per_day = 1
)

select
    date_day,
    subscription_id,
    customer_id,
    plan_id,
    daily_status,
    is_active_day,
    is_billable_day
from final
order by subscription_id, date_day;
