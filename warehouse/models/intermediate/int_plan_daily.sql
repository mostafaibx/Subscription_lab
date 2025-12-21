{{ config(materialized='view') }}

-- spine: Daily date dimension for generating one row per day
with spine as (
    select date_day
    from {{ ref('int_date_spine') }}
),

-- periods: Subscription active date boundaries to filter relevant days
periods as (
    select
        subscription_id,
        customer_id,
        active_from_date,
        active_to_date
    from {{ ref('int_subscription_periods') }}
),

-- plan_timeline: Plan change history with start/end dates for each plan period
plan_timeline as (
    select
        subscription_id,
        plan_id,
        plan_start_date,
        plan_end_date
    from {{ ref('int_plan_events_timeline') }}
),

-- subscription_days: Cartesian product creating one row per subscription per active day
subscription_days as (
    select
        spine.date_day,
        periods.subscription_id,
        periods.customer_id
    from spine
    inner join periods
        on spine.date_day >= periods.active_from_date
        and spine.date_day <= periods.active_to_date
),

-- daily_plan: Join plan timeline to find which plan was active on each day
daily_plan as (
    select
        subscription_days.date_day,
        subscription_days.subscription_id,
        subscription_days.customer_id,
        plan_timeline.plan_id
    from subscription_days
    left join plan_timeline
        on subscription_days.subscription_id = plan_timeline.subscription_id
        and subscription_days.date_day >= plan_timeline.plan_start_date
        and (plan_timeline.plan_end_date is null or subscription_days.date_day < plan_timeline.plan_end_date)
),

-- ranked_plan: Deduplicate in case of overlapping plan periods (defensive measure)
ranked_plan as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        row_number() over (
            partition by subscription_id, date_day
            order by plan_id desc nulls last
        ) as rank_per_day
    from daily_plan
),

-- final: Select top-ranked plan per day and filter out null plans
final as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id
    from ranked_plan
    where rank_per_day = 1
        and plan_id is not null
)

select
    date_day,
    subscription_id,
    customer_id,
    plan_id
from final
order by subscription_id, date_day;
