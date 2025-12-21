{{ config(materialized='view') }}

{# 
Combine two sources of subscription status data:
1. Event log - detailed history of status changes (priority 0 = higher priority)
2. Subscription table - current state snapshot at start date (priority 1 = lower priority)
The priority system ensures events win when deduplicating same-day records.
#}

{# 
Hybrid Event-Snapshot Pattern for SCD Type 2
Merges subscription events with current state, using priority-based
deduplication to generate complete status timeline segments.
#}

with event_source as (
    select
        event_id,
        subscription_id,
        coalesce(effective_date, date_trunc('day', occurred_at))::date as event_date,
        occurred_at,
        case
            when event_type in ('canceled', 'churned') then 'canceled'
            when event_type = 'paused' then 'paused'
            when event_type = 'payment_failed' then 'delinquent'
            when event_type in ('resumed', 'reactivated', 'created', 'payment_recovered') then 'active'
            else 'active'
        end as status,
        0 as source_priority
    from {{ ref('stg_subscription_events') }}

    union all

    select
        null as event_id,
        subscription_id,
        date_trunc('day', started_at)::date as event_date,
        started_at as occurred_at,
        status,
        1 as source_priority
    from {{ ref('stg_subscriptions') }}
    where subscription_id is not null and started_at is not null
),


unique_events as (
    select
        event_id,
        subscription_id,
        event_date,
        occurred_at,
        status,
        source_priority
    from (
        select *,
            row_number() over (
                partition by subscription_id, event_date
                order by source_priority, event_id desc nulls last
            ) as rank_per_day
        from event_source
        where event_date is not null
    ) flagged
    where rank_per_day = 1
),


status_intervals as (
    select
        subscription_id,
        status,
        event_date as status_start_date,
        lead(event_date) over (
            partition by subscription_id
            order by event_date, source_priority, occurred_at, event_id
        ) as status_end_date,
        event_id as status_event_id
    from unique_events
)

select
    status_intervals.subscription_id,
    case
        when status_intervals.status_end_date is null then coalesce(sub.status, status_intervals.status)
        else status_intervals.status
    end as status,
    status_start_date,
    status_end_date,
    status_event_id
from status_intervals
left join {{ ref('stg_subscriptions') }} sub
    on sub.subscription_id = status_intervals.subscription_id
where status_intervals.status_end_date is null or status_start_date < status_end_date
