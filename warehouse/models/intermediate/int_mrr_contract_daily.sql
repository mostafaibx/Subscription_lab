{{ config(materialized='view') }}

with status_daily as (
    select
        date_day,
        subscription_id,
        customer_id,
        daily_status,
        is_active_day
    from {{ ref('int_subscription_status_daily') }}
),
plan_daily as (
    select
        date_day,
        subscription_id,
        plan_id
    from {{ ref('int_plan_daily') }}
),
plans as (
    select
        plan_id,
        plan_name,
        mrr_equivalent,
        billing_frequency
    from {{ ref('stg_plans') }}
),
joined as (
    select
        status_daily.date_day,
        status_daily.subscription_id,
        status_daily.customer_id,
        plan_daily.plan_id,
        status_daily.daily_status,
        status_daily.is_active_day,
        plans.plan_name,
        plans.mrr_equivalent as plan_mrr,
        plans.billing_frequency
    from status_daily
    inner join plan_daily
        on status_daily.subscription_id = plan_daily.subscription_id
        and status_daily.date_day = plan_daily.date_day
    left join plans
        on plan_daily.plan_id = plans.plan_id
),
mrr_calculated as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        plan_name,
        billing_frequency,
        daily_status,
        is_active_day,
        plan_mrr,
        case
            when daily_status = 'active' then coalesce(plan_mrr, 0)
            else 0
        end as mrr
    from joined
),
final as (
    select
        date_day,
        subscription_id,
        customer_id,
        plan_id,
        plan_name,
        billing_frequency,
        daily_status,
        is_active_day,
        mrr
    from mrr_calculated
    where mrr >= 0
)

select
    date_day,
    subscription_id,
    customer_id,
    plan_id,
    plan_name,
    billing_frequency,
    daily_status,
    is_active_day,
    mrr
from final
order by subscription_id, date_day;
