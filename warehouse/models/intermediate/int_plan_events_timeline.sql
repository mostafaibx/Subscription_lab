{{ config(materialized='view') }}

-- plan_change_events: Extract plan upgrade/downgrade events from event log
with plan_change_events as (
    select
        event_id,
        subscription_id,
        customer_id,
        new_plan_id as plan_id,
        coalesce(effective_date, date_trunc('day', occurred_at))::date as plan_change_date,
        occurred_at,
        event_type,
        'plan_changed' as change_type
    from {{ ref('stg_subscription_events') }}
    where is_plan_change = true
),

-- creation_events: Extract initial plan assignment from subscription creation events
creation_events as (
    select
        event_id,
        subscription_id,
        customer_id,
        new_plan_id as plan_id,
        coalesce(effective_date, date_trunc('day', occurred_at))::date as plan_change_date,
        occurred_at,
        event_type,
        'created' as change_type
    from {{ ref('stg_subscription_events') }}
    where is_activation_event = true
        and new_plan_id is not null
),

-- subscription_seed: Fallback baseline plan from subscriptions table if events are missing
subscription_seed as (
    select
        null as event_id,
        subscription_id,
        customer_id,
        plan_id,
        date_trunc('day', started_at)::date as plan_change_date,
        started_at as occurred_at,
        'seed' as event_type,
        'created' as change_type
    from {{ ref('stg_subscriptions') }}
    where subscription_id is not null
        and started_at is not null
        and plan_id is not null
),

-- all_plan_events: Combine all three sources into single timeline
all_plan_events as (
    select * from plan_change_events
    union all
    select * from creation_events
    union all
    select * from subscription_seed
),

-- unique_plan_events: Deduplicate same-day plan changes, prioritizing plan_changed events over creation/seed
unique_plan_events as (
    select
        event_id,
        subscription_id,
        customer_id,
        plan_id,
        plan_change_date,
        occurred_at,
        change_type
    from (
        select *,
            row_number() over (
                partition by subscription_id, plan_change_date
                order by 
                    case when event_type = 'plan_changed' then 0
                         when event_type = 'created' then 1
                         else 2
                    end,
                    occurred_at,
                    event_id desc nulls last
            ) as rank_per_day
        from all_plan_events
        where plan_change_date is not null
    ) ranked
    where rank_per_day = 1
),

-- plan_intervals: Convert point-in-time events to time-bounded segments using LEAD window function
plan_intervals as (
    select
        subscription_id,
        customer_id,
        plan_id,
        plan_change_date as plan_start_date,
        lead(plan_change_date) over (
            partition by subscription_id
            order by plan_change_date, occurred_at, event_id
        ) as plan_end_date,
        change_type,
        event_id
    from unique_plan_events
)

select
    subscription_id,
    customer_id,
    plan_id,
    plan_start_date,
    plan_end_date,
    change_type,
    event_id as plan_event_id
from plan_intervals
where plan_end_date is null or plan_start_date < plan_end_date